from grafanalib.core import (
	Dashboard, Graph, GridPos,Templating, Template, Gauge, GaugePanel, Legend,
	GreaterThan, OP_AND, OPS_FORMAT, RowPanel, RTYPE_SUM, SECONDS_FORMAT,
	SHORT_FORMAT, single_y_axis, Target, TimeRange, YAxes, YAxis
)
from grafanalib._gen import (
	print_dashboard, DashboardEncoder
)
import json
import yaml

dashboard=Dashboard(
	title="DEV: Grafanalib-Components",
	templating=Templating(list=[
		Template(
			default="Thanos-Meta",
			name="datasource",
			type="datasource",
			query="prometheus"
		),
		Template(
			default="",
			multi=True,
			includeAll=True,
			name="Environment",
			dataSource="$datasource",
			query="label_values(env)"
		),
		Template(
			default="",
			multi=True,
			includeAll=True,
			name="Cluster",
			dataSource="$datasource",
			query="label_values(cluster)"
		),
		Template(
			name="Deployment",
			type="interval",
			query='"summary-reader","summary-writer","api","epoch-reader-1","epoch-reader-2","epoch-writer","front","gql","homeshard","ingestion-pipeline","queue","worker"'
		),
		Template(
			name="Node",
			includeAll=True,
			multi=True,
			dataSource="$datasource",
			query="label_values(kube_node_info, node)"
		)
	]),
	panels=[
		GaugePanel(
			title="Deployment memory usage",
			dataSource="$datasource",
			targets=[
				Target(
					expr='sum (container_memory_working_set_bytes{pod=~"$Environment-$Deployment.*$", node=~"^$Node$",env=~"^$Environment.*$",cluster=~"^$Cluster.*$"}) / sum (kube_node_status_allocatable{resource="memory",node=~"^$Node$",env=~"^$Environment.*$",cluster=~"^$Cluster.*$"}) * 100',
					refId="A",
				),
			],
			gridPos=GridPos(h=5,w=8,x=0,y=0)
		),
		GaugePanel(
			title="Deployment CPU usage",
			dataSource="$datasource",
			targets=[
				Target(
					expr='sum (rate (container_cpu_usage_seconds_total{pod=~"$Environment-$Deployment.*$",node=~"^$Node$",env=~"^$Environment.*$",cluster=~"^$Cluster.*$"}[1m])) / sum (kube_node_status_capacity{resource="cpu",node=~"^$Node$",env=~"^$Environment.*$",cluster=~"^$Cluster.*$"}) * 100',
					refId="A",
				),
			],
			gridPos=GridPos(h=5,w=8,x=8,y=0)
		),
		Graph(
			title="Deployment CPU Usage/Requests/Limits",
			dataSource="$datasource",
			targets=[
				Target(
					expr='avg(rate(container_cpu_usage_seconds_total{env=~"$Environment",cluster=~"^$Cluster",pod=~"$Environment-$Deployment.*", container=~"tomcat|summary"}[5m]))',
					refId="A",
					legendFormat="Average CPU Usage",
				),
				Target(
					expr='avg(kube_pod_container_resource_requests{resource="cpu",env=~"$Environment",cluster=~"^$Cluster",exported_pod=~"$Environment-$Deployment.*", exported_container=~"tomcat|summary"})',
					refId="B",
					legendFormat="CPU Requests"
				),
				Target(
					expr='avg(kube_pod_container_resource_limits{resource="cpu",env=~"$Environment",cluster=~"^$Cluster",exported_pod=~"$Environment-$Deployment.*", exported_container=~"tomcat|summary"})',
					refId="C",
					legendFormat="CPU Limits"
				),
				Target(
					expr='avg(rate(container_cpu_cfs_throttled_seconds_total{env=~"$Environment",cluster=~"^$Cluster",pod=~"$Environment-$Deployment.*", container=~"tomcat|summary"}[5m]))',
					refId="C",
					legendFormat="Average CPU throttling rate"
				),
			],
			gridPos=GridPos(h=8,w=24,x=0,y=6),
			legend=Legend(
				alignAsTable=True,
				max=True,
				min=True,
				current=True,
				avg=True,
				rightSide=True,
			)
		)
	]
).auto_panel_ids()

dashboard_json = json.dumps(dashboard.to_json_data(), sort_keys=True, indent=2, cls=DashboardEncoder)

base_crd_template = {'apiVersion': 'integreatly.org/v1alpha1', 'kind': 'GrafanaDashboard',
'metadata': {'namespace': 'grafana', 'name': 'dev-deployment', 'labels': {'dash': 'board'}}}

dashboard_yaml = {'spec': {'json': dashboard_json}}

with open("grafanadashboard/dev-dash-grafanadashboard.yaml", "a") as f:
	print(yaml.dump(base_crd_template, indent=2, default_flow_style=False), file=f)
	print(yaml.dump(dashboard_yaml, indent=2, default_flow_style=False), file=f)

with open("dashboard-json/components-dashboard.json", "a") as j:
	print(dashboard_json, file=j)
