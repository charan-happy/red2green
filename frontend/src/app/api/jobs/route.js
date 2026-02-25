export async function GET(request) {
  try {
    const response = await fetch('http://api:8000/api/jobs', {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    console.error('Error fetching jobs:', error);
    return Response.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
