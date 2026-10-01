FROM python:3.12-slim
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
CMD ["python", "-m", "github_mcp.main"]
