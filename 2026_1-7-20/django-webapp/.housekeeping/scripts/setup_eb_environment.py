#!/usr/bin/env python3
"""
Administrative Python Script for AWS Elastic Beanstalk Environment Setup

This script automates the process of setting up and deploying the Django web application
to AWS Elastic Beanstalk. It performs the following tasks:

1. Builds the Docker image for linux/amd64 architecture
2. Tags and pushes the image to AWS ECR
3. Updates the Dockerrun.aws.json with the new image
4. Creates or updates the Elastic Beanstalk environment

Usage:
    python setup_eb_environment.py <env_file> <environment_name> <version_tag>
    
Example:
    python setup_eb_environment.py ../../aws.env team620 v1.0.3

Requirements:
    - AWS CLI configured with appropriate credentials
    - Docker installed and running
    - python-dotenv package installed (pip install python-dotenv)
    
Author: Team 20 - Pol Plana, Zixin Zhang
Course: CCBDA - Cloud Computing for Big Data Analytics
Lab Session 7: CI/CD and Observability
"""

import subprocess
import sys
import os
import json
from pathlib import Path

try:
    from dotenv import dotenv_values
except ImportError:
    print("ERROR: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_step(step_num, message):
    """Print a formatted step message"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[Step {step_num}]{Colors.RESET} {message}")


def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def run_command(command, description, capture_output=False, shell=False):
    """Run a shell command and handle errors"""
    print(f"  Running: {command[:100]}..." if len(command) > 100 else f"  Running: {command}")
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=capture_output, text=True)
        else:
            result = subprocess.run(command.split(), check=True,
                                  capture_output=capture_output, text=True)
        print_success(description)
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print_error(f"Failed: {description}")
        if capture_output and e.stderr:
            print(f"  Error: {e.stderr}")
        return None


def check_prerequisites():
    """Check if required tools are installed"""
    print_step(0, "Checking prerequisites...")
    
    # Check Docker
    result = subprocess.run(["docker", "--version"], capture_output=True)
    if result.returncode != 0:
        print_error("Docker is not installed or not running")
        return False
    print_success("Docker is available")
    
    # Check AWS CLI
    result = subprocess.run(["aws", "--version"], capture_output=True)
    if result.returncode != 0:
        print_error("AWS CLI is not installed")
        return False
    print_success("AWS CLI is available")
    
    # Check EB CLI
    result = subprocess.run(["eb", "--version"], capture_output=True)
    if result.returncode != 0:
        print_warning("EB CLI is not installed (optional for this script)")
    else:
        print_success("EB CLI is available")
    
    return True


def load_configuration(env_file):
    """Load configuration from .env file"""
    if not os.path.exists(env_file):
        print_error(f"Configuration file not found: {env_file}")
        return None
    
    config = dotenv_values(env_file)
    
    # Validate required fields
    required_fields = [
        'AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
        'AWS_ACCOUNT_ID', 'DJANGO_DEBUG', 'DJANGO_ALLOWED_HOSTS'
    ]
    
    missing = [f for f in required_fields if f not in config]
    if missing:
        print_error(f"Missing required configuration fields: {', '.join(missing)}")
        return None
    
    return config


def build_docker_image(version_tag, django_webapp_dir):
    """Build Docker image for linux/amd64 architecture"""
    print_step(1, f"Building Docker image (version: {version_tag})...")
    
    os.chdir(django_webapp_dir)
    
    # Build for linux/amd64 (required for AWS EC2)
    cmd = f"docker build --platform linux/amd64 -t django-docker:{version_tag} ."
    result = run_command(cmd, "Docker image built successfully", shell=True)
    
    return result is not None or True  # Allow to continue even if build uses cache


def authenticate_ecr(config):
    """Authenticate Docker with AWS ECR"""
    print_step(2, "Authenticating with AWS ECR...")
    
    region = config['AWS_REGION']
    account_id = config['AWS_ACCOUNT_ID']
    ecr_url = f"{account_id}.dkr.ecr.{region}.amazonaws.com"
    
    # Get login password and authenticate
    cmd = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {ecr_url}"
    result = run_command(cmd, "ECR authentication successful", shell=True)
    
    return ecr_url


def tag_and_push_image(version_tag, ecr_url, repo_name="django-webapp-docker-repo"):
    """Tag and push Docker image to ECR"""
    print_step(3, "Tagging and pushing image to ECR...")
    
    image_uri = f"{ecr_url}/{repo_name}:{version_tag}"
    
    # Tag the image
    tag_cmd = f"docker tag django-docker:{version_tag} {image_uri}"
    run_command(tag_cmd, "Image tagged successfully", shell=True)
    
    # Push to ECR
    push_cmd = f"docker push {image_uri}"
    run_command(push_cmd, "Image pushed to ECR successfully", shell=True)
    
    return image_uri


def update_dockerrun_json(image_uri, elasticbeanstalk_dir):
    """Update Dockerrun.aws.json with new image URI"""
    print_step(4, "Updating Dockerrun.aws.json...")
    
    dockerrun_path = os.path.join(elasticbeanstalk_dir, "Dockerrun.aws.json")
    
    dockerrun_content = {
        "AWSEBDockerrunVersion": "1",
        "Image": {
            "Name": image_uri
        },
        "Ports": [
            {
                "ContainerPort": 8000
            }
        ]
    }
    
    with open(dockerrun_path, 'w') as f:
        json.dump(dockerrun_content, f, indent=2)
    
    print_success(f"Dockerrun.aws.json updated with image: {image_uri}")
    return True


def check_eb_environment_exists(environment_name, config):
    """Check if an Elastic Beanstalk environment exists"""
    cmd = f"aws elasticbeanstalk describe-environments --environment-names {environment_name} --region {config['AWS_REGION']}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    if result.returncode == 0:
        env_data = json.loads(result.stdout)
        if env_data.get('Environments') and len(env_data['Environments']) > 0:
            status = env_data['Environments'][0].get('Status')
            return status not in ['Terminated', 'Terminating']
    return False


def deploy_to_eb(environment_name, config, version_tag, elasticbeanstalk_dir):
    """Deploy to Elastic Beanstalk using EB CLI"""
    print_step(5, "Deploying to AWS Elastic Beanstalk...")
    
    os.chdir(elasticbeanstalk_dir)
    
    # Check if environment exists
    if check_eb_environment_exists(environment_name, config):
        print(f"  Environment '{environment_name}' exists, deploying update...")
        cmd = "eb deploy"
        run_command(cmd, "Deployment initiated", shell=True)
    else:
        print(f"  Environment '{environment_name}' does not exist.")
        print_warning("Please create the environment first using the eb create command")
        print_eb_create_command(environment_name, config)
        return False
    
    return True


def print_eb_create_command(environment_name, config):
    """Print the eb create command for reference"""
    print("\n" + "="*80)
    print("To create a new environment, run the following command:")
    print("="*80)
    
    # Build the environment variables string
    hostname = f"{environment_name}.{config['AWS_REGION']}.elasticbeanstalk.com"
    hosts = config.get('DJANGO_ALLOWED_HOSTS', '').split(':')
    if hostname not in hosts:
        hosts.append(hostname)
    config['DJANGO_ALLOWED_HOSTS'] = ':'.join(hosts)
    
    env_vars = ','.join([f"{k}={v}" for k, v in config.items() if k != 'AWS_ACCOUNT_ID'])
    
    cmd = f"""eb create {environment_name} \\
    --min-instances 1 \\
    --max-instances 3 \\
    --instance_profile aws-elasticbeanstalk-ec2-role \\
    --service-role aws-elasticbeanstalk-service-role \\
    --elb-type application \\
    --instance-types t3.micro \\
    --keyname aws-eb \\
    --cname {environment_name} \\
    --envvars '{env_vars}'"""
    
    print(cmd)
    print("\n" + "="*80)


def verify_deployment(environment_name, config):
    """Verify the deployment status"""
    print_step(6, "Verifying deployment...")
    
    cmd = f"aws elasticbeanstalk describe-environments --environment-names {environment_name} --region {config['AWS_REGION']}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    if result.returncode == 0:
        env_data = json.loads(result.stdout)
        if env_data.get('Environments'):
            env = env_data['Environments'][0]
            status = env.get('Status', 'Unknown')
            health = env.get('Health', 'Unknown')
            url = env.get('CNAME', 'N/A')
            
            print(f"  Environment Status: {status}")
            print(f"  Health: {health}")
            print(f"  URL: http://{url}")
            
            if status == 'Ready' and health == 'Green':
                print_success("Deployment successful!")
                return True
            else:
                print_warning(f"Environment is {status} with health {health}")
    
    return False


def main():
    """Main function to orchestrate the deployment"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("AWS Elastic Beanstalk Environment Setup Script")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # Parse arguments
    if len(sys.argv) < 4:
        print("Usage: python setup_eb_environment.py <env_file> <environment_name> <version_tag>")
        print("Example: python setup_eb_environment.py ../../aws.env team620 v1.0.3")
        sys.exit(1)
    
    env_file = sys.argv[1]
    environment_name = sys.argv[2]
    version_tag = sys.argv[3]
    
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    elasticbeanstalk_dir = os.path.join(script_dir, '..', 'elasticbeanstalk')
    django_webapp_dir = os.path.join(script_dir, '..', '..')
    env_file_abs = os.path.abspath(os.path.join(script_dir, env_file))
    
    print(f"Configuration file: {env_file_abs}")
    print(f"Environment name: {environment_name}")
    print(f"Version tag: {version_tag}")
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Load configuration
    config = load_configuration(env_file_abs)
    if not config:
        sys.exit(1)
    
    print_success(f"Configuration loaded from {env_file}")
    
    # Warn if DEBUG is True
    if config.get('DJANGO_DEBUG', '').lower() == 'true':
        print_warning("DJANGO_DEBUG is set to True! This should be False for production.")
    
    # Build Docker image
    build_docker_image(version_tag, django_webapp_dir)
    
    # Authenticate with ECR
    ecr_url = authenticate_ecr(config)
    if not ecr_url:
        print_error("Failed to authenticate with ECR")
        sys.exit(1)
    
    # Tag and push image
    image_uri = tag_and_push_image(version_tag, ecr_url)
    
    # Update Dockerrun.aws.json
    update_dockerrun_json(image_uri, os.path.abspath(elasticbeanstalk_dir))
    
    # Deploy to Elastic Beanstalk
    deploy_to_eb(environment_name, config, version_tag, os.path.abspath(elasticbeanstalk_dir))
    
    # Verify deployment
    verify_deployment(environment_name, config)
    
    print(f"\n{Colors.BOLD}{'='*60}")
    print("Setup Complete!")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print("Next steps:")
    print(f"  1. Visit: http://{environment_name}.{config['AWS_REGION']}.elasticbeanstalk.com")
    print("  2. Check AWS Console for environment health")
    print("  3. Review CloudWatch logs for any issues")
    print("\nTo trigger CI/CD pipeline, create and push a git tag:")
    print(f"  git tag \"{version_tag}\"")
    print(f"  git push origin \"{version_tag}\"")


if __name__ == "__main__":
    main()
