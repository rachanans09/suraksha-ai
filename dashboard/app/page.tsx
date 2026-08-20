'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface CallRecord {
  id: string;
  created_at: string;
  sender_number: string;
  risk: 'low' | 'medium' | 'high';
  confidence?: number;
  reason: string;
}

export default function Dashboard() {
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  async function fetchCalls() {
    setLoading(true);
    const { data, error } = await supabase
      .from('calls')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching Supabase calls:', error.message);
    } else if (data) {
      setCalls(data);
    }
    setLoading(false);
  }

  useEffect(() => {
    fetchCalls();
  }, []);

  const badgeColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
      default:
        return 'bg-green-100 text-green-700 border-green-300';
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Top Navigation / Status */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              SuRaksha AI — Family Protection Dashboard
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Live scam call logs and risk evaluations.
            </p>
          </div>
          <button
            onClick={fetchCalls}
            className="px-4 py-2 text-sm font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition"
          >
            Refresh Calls
          </button>
        </div>

        {/* Calls Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100/75 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase">
                <tr>
                  <th className="p-4">Time</th>
                  <th className="p-4">Sender</th>
                  <th className="p-4">Risk Badge</th>
                  <th className="p-4">Confidence</th>
                  <th className="p-4">Reason / Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {calls.map((call) => (
                  <tr key={call.id} className="hover:bg-slate-50 transition">
                    <td className="p-4 text-slate-500 whitespace-nowrap">
                      {new Date(call.created_at).toLocaleString()}
                    </td>
                    <td className="p-4 font-mono font-medium text-slate-800">
                      {call.sender_number}
                    </td>
                    <td className="p-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeColor(
                          call.risk
                        )}`}
                      >
                        {call.risk?.toUpperCase() || 'UNKNOWN'}
                      </span>
                    </td>
                    <td className="p-4 text-slate-600 font-medium">
                      {call.confidence ? `${Math.round(call.confidence * 100)}%` : '—'}
                    </td>
                    <td className="p-4 text-slate-700 max-w-md">
                      {call.reason || 'No analysis details provided.'}
                    </td>
                  </tr>
                ))}

                {calls.length === 0 && !loading && (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-slate-400">
                      No call records logged yet.
                    </td>
                  </tr>
                )}

                {loading && (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-slate-400">
                      Loading call logs...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </main>
  );
}