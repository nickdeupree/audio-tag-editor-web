import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { BatchProvider } from "./vars/isBatch";
import { AppThemeProvider } from "./lib/ThemeProvider";
import { FilesProvider } from "./vars/files";
import { CurrentFileIndexProvider } from "./vars/currentFileIndex";
import { AllFilesMetadataProvider } from "./vars/allFilesMetadata";
import { AddingFileProvider } from "./vars/addingFile";
import { ThemeContextProvider } from "./contexts/ThemeContext";
import { ThemeSync } from "./components/ThemeSync";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Audio Tag Editor",
  description: "Edit Audio Tags",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {  return (
    <html lang="en">
      <head>
        <meta name="emotion-insertion-point" content="" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}      >        <ThemeContextProvider>
          <ThemeSync />
          <AppThemeProvider>
            <BatchProvider>
              <FilesProvider>
                <CurrentFileIndexProvider>
                  <AllFilesMetadataProvider>
                    <AddingFileProvider>
                      {children}
                    </AddingFileProvider>
                  </AllFilesMetadataProvider>
                </CurrentFileIndexProvider>
              </FilesProvider>
            </BatchProvider>
          </AppThemeProvider>
        </ThemeContextProvider>
      </body>
    </html>
  );
}
