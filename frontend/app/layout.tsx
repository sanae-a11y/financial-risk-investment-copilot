import './globals.css';
export const metadata = { title: 'Financial Risk & Investment Copilot', description: 'Agentic AI portfolio decision-support platform' };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
