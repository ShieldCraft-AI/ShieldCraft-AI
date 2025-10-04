#!/bin/bash
# Get CloudFront distribution domain for docs-site

echo "🔍 Searching for CloudFront distributions..."
echo ""

# Get all CloudFront distributions
aws cloudfront list-distributions \
  --query 'DistributionList.Items[*].[Id,DomainName,Comment,Enabled]' \
  --output table

echo ""
echo "📝 Your CloudFront domain is shown above in the 'DomainName' column"
echo "   It should look like: d123abc456def.cloudfront.net"
echo ""
echo "If you have a custom domain (CNAME), check:"
aws cloudfront list-distributions \
  --query 'DistributionList.Items[*].[Id,DomainName,Aliases.Items]' \
  --output json
