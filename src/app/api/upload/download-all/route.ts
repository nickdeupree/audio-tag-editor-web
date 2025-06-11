import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Forward the request to the Python backend
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 
      (process.env.NODE_ENV === 'production' 
        ? 'https://audio-tag-editor-web.onrender.com' 
        : 'http://localhost:8000');
    
    const response = await fetch(`${pythonBackendUrl}/upload/download-all`, {
      method: 'GET',
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Python backend error:', response.status, errorText);
      
      return NextResponse.json(
        { error: 'No files available for download' }, 
        { status: response.status }
      );
    }

    // Stream the zip file back
    const blob = await response.blob();
    const headers = new Headers();
    
    // Copy relevant headers from the backend response
    const contentDisposition = response.headers.get('content-disposition');
    if (contentDisposition) {
      headers.set('content-disposition', contentDisposition);
    }
    
    const contentType = response.headers.get('content-type') || 'application/zip';
    headers.set('content-type', contentType);
    
    return new NextResponse(blob, {
      status: response.status,
      headers: headers,
    });

  } catch (error) {
    console.error('Error downloading all files:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
