
# generate a single-purpose ssh key, not anticipated to need
# resource "local_file" "default" {
#   filename          = "../ansible/id_rsa_default"
#   file_permission   = "0700"
#   sensitive_content = tls_private_key.default.private_key_pem
# }

# resource "local_file" "default_pub" {
#   filename          = "../ansible/id_rsa_default.pub"
#   file_permission   = "0666"
#   sensitive_content = tls_private_key.default.public_key_openssh
# }

resource "aws_key_pair" "default" {
  key_name   = "default-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCy1CDRSzg9DEVZQ5fze52rjl6HjeiXFUQogKVR838mCrojPeHIeM/HYZ2ten7zFZ9vpwLA3hBf+z92FwN6lM4jEEz4VU15QDRFcLtEnsstOfp10sR0Kbnc7PhV79IlyYkRtHBDlW7unGbflIrFAA6PzQklFGJrGH/9unRcRkFLlOPd4MCiU3kORK+yDrDmDn+aT9ajHTY6XvjiYqWF3ThzXuvo1nRccb3SBvCddmi2MKoMPPq5Z6dJqDJkdWy9UXcT3QlsXE6XUL2GuL6oZ/e10mAad74VvtUAII7p7tHSLhZbrp+92MXq2dYC/wJapJZdXbEpycgcq2BmeKdKaqkF calebgosnell@Calebs-MacBook-Pro.local"
}

resource "aws_eip" "sudoku_ip" {
  vpc = true
}

resource "aws_eip_association" "sudoku_ip" {
  instance_id   = aws_instance.sudoku.id
  allocation_id = aws_eip.sudoku_ip.id
}

resource "aws_instance" "sudoku" {
  instance_type          = "t4g.medium"
  ami                    = "ami-0a82127206c2824a1" # ubuntu 20.04
  subnet_id              = module.vpc.public_subnets[2]
  vpc_security_group_ids = [aws_security_group.sg_sudoku.id]
  key_name               = "default-key" # aws_key_pair.default.key_name

  root_block_device {
    encrypted   = true
    volume_size = "50"
    volume_type = "gp3"
  }
  volume_tags = {
    Name = "sudoku"
  }
  tags = {
    Name = "sudoku"
  }
}

resource "local_file" "ansible_inventory" {
  filename        = "../ansible/inventory-terraform"
  file_permission = "0644"
  content         = <<EOF
[all]
${aws_eip.sudoku_ip.public_ip} ansible_user=ubuntu
EOF
}

resource "aws_security_group" "sg_sudoku" {
  name        = "sudoku"
  description = "Access for ftp instances"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port        = "22"
    to_port          = "22"
    protocol         = "tcp"
    cidr_blocks      = [
      "47.227.66.10/32",
       "174.202.71.24/32",
       "198.102.151.243/32"]
    # ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port        = "80"
    to_port          = "80"
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port        = "443"
    to_port          = "443"
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port        = "8443"
    to_port          = "8443"
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = "0"
    to_port          = "0"
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}
