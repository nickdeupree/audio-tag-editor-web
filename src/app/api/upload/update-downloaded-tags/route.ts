import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Get the form data from the request
    const formData = await request.formData();    // Forward the request to the Python backend
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'https://audio-tag-editor-web.onrender.com';
    
    const response = await fetch(`${pythonBackendUrl}/upload/update-downloaded-tags`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Python backend error:', response.status, errorText);
      
      try {
        const errorJson = JSON.parse(errorText);
        return NextResponse.json(
          { error: errorJson.detail || 'Failed to update downloaded file metadata' }, 
          { status: response.status }
        );
      } catch {
        return NextResponse.json(
          { error: errorText || 'Failed to update downloaded file metadata' }, 
          { status: response.status }
        );
      }
    }

    // For downloaded files, we expect a JSON response instead of a blob
    const responseData = await response.json();
    
    return NextResponse.json(responseData);

  } catch (error) {
    console.error('Error updating downloaded file metadata:', error);
    return NextResponse.json(
      { error: 'Internal server error' }, 
      { status: 500 }
    );
  }
}
