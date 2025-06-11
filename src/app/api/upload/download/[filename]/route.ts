import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { filename: string } }
) {
  try {
    const filename = params.filename;

    // Forward the request to the Python backend
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 
      (process.env.NODE_ENV === 'production' 
        ? 'https://audio-tag-editor-web.onrender.com' 
        : 'http://localhost:8000');
    
    const response = await fetch(`${pythonBackendUrl}/upload/download/${filename}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Python backend error:', response.status, errorText);
      
      return NextResponse.json(
        { error: 'File not found' }, 
        { status: response.status }
      );
    }

    // Stream the file back
    const blob = await response.blob();
    const headers = new Headers();
    
    // Copy relevant headers from the backend response
    const contentDisposition = response.headers.get('content-disposition');
    if (contentDisposition) {
      headers.set('content-disposition', contentDisposition);
    }
    
    const contentType = response.headers.get('content-type') || 'audio/mpeg';
    headers.set('content-type', contentType);
    
    return new NextResponse(blob, {
      status: response.status,
      headers: headers,
    });

  } catch (error) {
    console.error('Error downloading file:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
