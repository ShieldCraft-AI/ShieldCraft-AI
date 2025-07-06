from diagrams import Cluster, Diagram
from diagrams.aws.network import (
    VPC,
    PrivateSubnet,
    PublicSubnet,
    NATGateway,
    InternetGateway,
)
from diagrams.generic.network import Firewall, Router
from diagrams.aws.management import Cloudwatch
from diagrams.custom import Custom

graph_attr = {
    "fontsize": "16",
    "fontname": "Helvetica",
    "pad": "1.2",  # More breathing room
    "dpi": "400",  # Sharper image
    "margin": "0.75",
    "splines": "spline",  # Smooth curved arrows
    "ranksep": "1.8",  # Vertical spacing
    "nodesep": "1.5",  # Horizontal spacing
    "layout": "dot",
    "labelloc": "t",  # Cluster labels on top
    "bgcolor": "white",  # Clean background
}

node_attr = {
    "fontname": "Helvetica",
    "fontsize": "13",
    "width": "1.4",
    "height": "1.0",
    "shape": "box",
    "style": "filled",
    "fillcolor": "white",
}

with Diagram(
    "Networking & Security Architecture",
    direction="LR",  # Horizontal layout is better for networking flows
    show=False,
    filename="networking_architecture",
    outformat="png",  # Or 'svg' for vector output
    graph_attr=graph_attr,
    node_attr=node_attr,
):
    with Cluster("Amazon VPC"):
        vpc = VPC("VPC\n(10.0.0.0/16)")

        with Cluster("Public Subnet"):
            igw = InternetGateway("Internet Gateway")
            public_subnet = PublicSubnet("Public Subnet 1")
            nat_gw = NATGateway("NAT Gateway")
            sg_public = Firewall("Public SG")

        with Cluster("Private Subnet"):
            private_subnet = PrivateSubnet("Private Subnet 1")
            sg_private = Firewall("Private SG")
            vpc_endpoint = Custom("VPC Endpoint", "./icons/vpc_endpoint.png")

        with Cluster("Routing"):
            rt_public = Router("Public Route Table")
            rt_private = Router("Private Route Table")

        flow_logs = Cloudwatch("VPC Flow Logs")

        # Connections
        igw >> public_subnet
        public_subnet >> nat_gw >> private_subnet
        vpc >> [public_subnet, private_subnet]
        public_subnet >> rt_public
        private_subnet >> rt_private
        private_subnet >> vpc_endpoint
        [public_subnet, private_subnet] >> flow_logs
        public_subnet >> sg_public
        private_subnet >> sg_private
