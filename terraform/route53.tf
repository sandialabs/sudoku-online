



# data "aws_route53_zone" "sixfeetup_com_zone" {
#   provider = aws.utility
#   name     = "sixfeetup.com"
# }

# resource "aws_route53_record" "sudoku" {
#   provider = aws.utility
#   zone_id  = data.aws_route53_zone.sixfeetup_com_zone.zone_id
#   name     = "sandia-sudoku"
#   type     = "A"
#   ttl      = 500
#   records  = [aws_eip.sudoku_ip.public_ip]
# }
