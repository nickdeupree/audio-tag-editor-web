import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const files = formData.getAll('files') as File[];

    if (!files || files.length === 0) {
      return NextResponse.json({ error: 'No files uploaded' }, { status: 400 });
    }

    // Create a new FormData to send to Python backend
    const backendFormData = new FormData();
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      backendFormData.append('files', file);
    }    // Send files to Python backend
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'https://audio-tag-editor-web.onrender.com';
    
    const response = await fetch(`${pythonBackendUrl}/upload`, {
      method: 'POST',
      body: backendFormData,
    });

    if (!response.ok) {
      throw new Error(`Python backend responded with status: ${response.status}`);
    }

    const result = await response.json();
    
    return NextResponse.json({ 
      success: true, 
      message: 'Files uploaded successfully',
      backendResponse: result 
    });

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Failed to upload files' }, 
      { status: 500 }
    );
  }
}