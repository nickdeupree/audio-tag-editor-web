import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Get the form data from the request
    const formData = await request.formData();
    const storedFilename = formData.get('stored_filename') as string;
    
    if (!storedFilename) {
      return NextResponse.json(
        { error: 'Missing stored_filename parameter' }, 
        { status: 400 }
      );
    }

    // Remove stored_filename from formData since it goes in the URL path
    formData.delete('stored_filename');

    // Forward the request to the Python backend
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 
      (process.env.NODE_ENV === 'production' 
        ? 'https://audio-tag-editor-web.onrender.com' 
        : 'http://localhost:8000');
    
    const response = await fetch(`${pythonBackendUrl}/upload/update-tags-workspace/${encodeURIComponent(storedFilename)}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Python backend error:', response.status, errorText);
      
      try {
        const errorJson = JSON.parse(errorText);
        return NextResponse.json(
          { error: errorJson.detail || 'Failed to update workspace file metadata' }, 
          { status: response.status }
        );
      } catch {
        return NextResponse.json(
          { error: errorText || 'Failed to update workspace file metadata' }, 
          { status: response.status }
        );
      }
    }

    // For workspace files, we expect a JSON response
    const responseData = await response.json();
    
    return NextResponse.json(responseData);

  } catch (error) {
    console.error('Error updating workspace file metadata:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
