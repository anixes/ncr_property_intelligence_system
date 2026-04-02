'use client';
import { useEffect } from 'react';

export default function DebugData({ data }: { data: any }) {
  useEffect(() => {
    console.log('DEBUG_DATA_LAT_LON:', data?.map((l: any) => ({ lat: l.latitude, lon: l.longitude })));
  }, [data]);
  return null;
}
