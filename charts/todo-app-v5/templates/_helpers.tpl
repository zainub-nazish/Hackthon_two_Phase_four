{{/*
Task ID  : T006
Helm helper templates for todo-app-v5
*/}}

{{/*
Expand image reference. Uses global registry prefix if set.
*/}}
{{- define "todo.image" -}}
{{- $reg := .Values.global.registry -}}
{{- $name := .image -}}
{{- $tag := .Values.global.imageTag -}}
{{- if $reg -}}
{{ $reg }}/{{ $name }}:{{ $tag }}
{{- else -}}
{{ $name }}:{{ $tag }}
{{- end -}}
{{- end }}

{{/*
Common Dapr annotations for a service pod.
Usage: include "todo.daprAnnotations" (dict "appId" .Values.backend.daprAppId "appPort" .Values.backend.daprAppPort "Values" .Values)
*/}}
{{- define "todo.daprAnnotations" -}}
dapr.io/enabled: "true"
dapr.io/app-id: {{ .appId | quote }}
dapr.io/app-port: {{ .appPort | quote }}
dapr.io/log-level: {{ .Values.dapr.logLevel | quote }}
dapr.io/sidecar-cpu-request: "50m"
dapr.io/sidecar-memory-request: "64Mi"
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo.labels" -}}
app.kubernetes.io/managed-by: Helm
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
phase: "v5"
{{- end }}
