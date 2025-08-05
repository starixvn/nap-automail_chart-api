from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from typing import Optional
import uvicorn
import threading
from dhwl import safe_render_dhwl_chart, DHWLChartRequest

# Khởi tạo FastAPI app
app = FastAPI(
    title="Hello World API",
    description="A simple Hello World API built with FastAPI",
    version="1.0.0"
)

# Thread lock to ensure the thread-safety for endpoint /dhwl
chart_render_lock = threading.Lock()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Python Chart API!", "status": "running"}

# Health check endpoint
@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "Python Chart API"}

# DHWL chart endpoint
@app.post("/dhwl")
async def generate_dhwl_chart(request: DHWLChartRequest):
    """
    Generate DHWL chart from provided data
    
    Args:
        request: DHWLChartRequest containing sb_data, total_data, month, and year
        
    Returns:
        PNG image bytes
    """
    try:        
        with chart_render_lock:
            # Convert year to string if it's an integer
            year_str = str(request.year)
            
            # Call the render function to get image bytes
            image_bytes = safe_render_dhwl_chart(
                sb_data=request.sb_data,
                total_data=request.total_data,
                month=request.month,
                year=year_str
            )
            
            # Return the image bytes as PNG response
            return Response(
                content=image_bytes,
                media_type="image/png",
                headers={"Content-Disposition": "attachment; filename=dhwl_chart.png"}
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000) 