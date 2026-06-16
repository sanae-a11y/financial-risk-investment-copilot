'use client';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';
export default function PriceChart({ data }: { data: any[] }) {
  return <div className="chart"><ResponsiveContainer width="100%" height={240}><LineChart data={data}><XAxis dataKey="date" hide/><YAxis domain={["auto","auto"]}/><Tooltip/><Line type="monotone" dataKey="price" strokeWidth={3} dot={false}/></LineChart></ResponsiveContainer></div>;
}
