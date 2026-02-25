export const metadata = {
  title: 'PatchPilot Dashboard',
  description: 'PatchPilot monitoring dashboard',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>{`
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body { background: #0B0F1A; color: #E5E7EB; font-family: system-ui; }
        `}</style>
      </head>
      <body>
        <div id="root">{children}</div>
      </body>
    </html>
  );
}
