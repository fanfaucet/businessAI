JOB_TEMPLATE = """apiVersion: batch/v1
kind: Job
metadata:
  name: annaban-benchmark
spec:
  template:
    spec:
      containers:
      - name: runner
        image: annaban/benchmark:latest
        resources:
          limits:
            cpu: \"2\"
            memory: \"4Gi\"
        env:
        - name: AGS_SCORE
          value: \"{annaban_governance_score}\"
      restartPolicy: Never
"""
