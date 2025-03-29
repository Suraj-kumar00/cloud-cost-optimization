# Create a VPC
resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "My-VPC"
  }
}

# Create a Public Subnet
resource "aws_subnet" "my_subnet" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-south-1a" 
  map_public_ip_on_launch = true

  tags = {
    Name = "My-Subnet"
  }
}

# Create an Internet Gateway
resource "aws_internet_gateway" "my_igw" {
  vpc_id = aws_vpc.my_vpc.id

  tags = {
    Name = "My-Internet-Gateway"
  }
}

# Create a Route Table for Public Subnet
resource "aws_route_table" "my_route_table" {
  vpc_id = aws_vpc.my_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.my_igw.id
  }

  tags = {
    Name = "My-Route-Table"
  }
}

# Associate Route Table with Public Subnet
resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.my_subnet.id
  route_table_id = aws_route_table.my_route_table.id
}

# Create a Security Group
resource "aws_security_group" "my_sg" {
  vpc_id = aws_vpc.my_vpc.id

  # Allow SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  # Allow all Outbound Traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "My-Security-Group"
  }
}

# Create an EC2 Instance
resource "aws_instance" "cost_optimized_ec2" {
  ami                    = "ami-0e35ddab05955cf57"
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.my_subnet.id
  vpc_security_group_ids = [aws_security_group.my_sg.id]

  tags = {
    Name = "Cost-Optimized-EC2"
  }
}

# Create an EBS Volume
resource "aws_ebs_volume" "my_volume" {
  availability_zone = "ap-south-1a"  
  size             = 10

  tags = {
    Name = "My-EBS-Volume"
  }
}

# Attach EBS Volume to EC2
resource "aws_volume_attachment" "ebs_attach" {
  device_name = "/dev/xvdf"
  volume_id   = aws_ebs_volume.my_volume.id
  instance_id = aws_instance.cost_optimized_ec2.id
}

# Create an EBS Snapshot (initial backup)
resource "aws_ebs_snapshot" "initial_snapshot" {
  volume_id = aws_ebs_volume.my_volume.id

  tags = {
    Name = "Initial-Snapshot"
  }

  # ✅ Ensure the volume exists before creating the snapshot
  depends_on = [aws_volume_attachment.ebs_attach]
}
