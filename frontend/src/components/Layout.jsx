import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { TopProgressBar } from '../design-system';

export const Layout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-blue-500 selection:text-white">
      <TopProgressBar />
      <Navbar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Outlet />
      </main>
      <footer className="bg-white border-t border-slate-200/80 text-slate-500 py-6 text-xs text-center">
        <div className="max-w-7xl mx-auto px-4">
          <p className="font-semibold text-slate-700">
            Legal Metrology Compliance Enforcement System — Government of India
          </p>
          <p className="mt-1 text-slate-400">
            RapidOCR + Tesseract Dual Consensus Engine · ELA Forensic Tamper Detection · Bharatiya Sakshya Adhiniyam, 2023 §63 Certified
          </p>
        </div>
      </footer>
    </div>
  );
};
export default Layout;
