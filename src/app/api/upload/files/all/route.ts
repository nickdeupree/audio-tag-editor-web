import { NextRequest, NextResponse } from 'next/server';
import { API_CONFIG } from '@/app/config/api';

export async function GET(request: NextRequest) {
  try {
    console.log('Fetching all files...');
    
    const response = await fetch(`${API_CONFIG.DIRECT_BACKEND_URL}/upload/files/all`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend get all files error:', errorText);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Files fetched successfully:', {
      total: result.total_files,
      updated: result.updated_files,
      downloaded: result.downloaded_files
    });

    return NextResponse.json(result);
  } catch (error) {
    console.error('Get all files error:', error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
