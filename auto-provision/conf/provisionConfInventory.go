package conf

const TemplateInventory = `[all]
{{- range $_, $host := .DeployHost}}
{{$host.Ip}} ansible_ssh_user={{$host.Username}} ansible_ssh_pass={{$host.Password}} 
{{- end}}

[controller]
{{- range $_, $host := .DeployHost}}
{{- if strcontains $host.Name "controller"  }}
{{$host.Ip}} ansible_ssh_user={{$host.Username}} ansible_ssh_pass={{$host.Password}} 
{{- end}}
{{- end}}

[node]
{{- range $_, $host := .DeployHost}}
{{- if strcontains $host.Name "node"}}
{{$host.Ip}} ansible_ssh_user={{$host.Username}} ansible_ssh_pass={{$host.Password}} 
{{- end}}
{{- end}}
`
