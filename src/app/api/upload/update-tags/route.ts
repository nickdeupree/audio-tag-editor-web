import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Get the form data from the request
    const formData = await request.formData();    // Forward the request to the Python backend
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 
      (process.env.NODE_ENV === 'production' 
        ? 'https://audio-tag-editor-web.onrender.com' 
        : 'http://localhost:8000');
    
    const response = await fetch(`${pythonBackendUrl}/upload/update-tags`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Python backend error:', response.status, errorText);
      
      try {
        const errorJson = JSON.parse(errorText);
        return NextResponse.json(
          { error: errorJson.detail || 'Failed to update metadata' }, 
          { status: response.status }
        );
      } catch {
        return NextResponse.json(
          { error: errorText || 'Failed to update metadata' }, 
          { status: response.status }
        );
      }
    }

    // Get the response content type and data
    const contentType = response.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      // If JSON response, parse and return it
      const result = await response.json();
      return NextResponse.json(result);
    } else {
      // If binary response (audio file), stream it back
      const blob = await response.blob();
      const headers = new Headers();
      
      // Copy relevant headers from the backend response
      const contentDisposition = response.headers.get('content-disposition');
      if (contentDisposition) {
        headers.set('content-disposition', contentDisposition);
      }
      
      headers.set('content-type', contentType);
      
      return new NextResponse(blob, {
        status: response.status,
        headers: headers,
      });
    }

  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
