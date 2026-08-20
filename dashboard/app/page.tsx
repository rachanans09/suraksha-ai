'use client';

import { useEffect, useState } from 'react';
import { getSupabase } from '../lib/supabaseClient';

interface CallRecord {
  id: number;
  created_at: string;
  sender_number: string | null;
  risk: string | null;
  confidence: number | null;
  reason: string | null;
}

export default function Dashboard() {
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchCalls = async () => {
    try {
      setLoading(true);
      const supabase = getSupabase();
      const { data, error } = await supabase
        .from('calls')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching calls:', error);
      } else if (data) {
        setCalls(data);
      }
    } catch (err) {
      console.error('Supabase query error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCalls();
  }, []);

  const getBadgeClass = (risk: string | null) => {
    const r = (risk || '').toLowerCase();
    if (r === 'high') return 'bg-red-100 text-red-700 border-red-300';
    if (r === 'medium') return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-green-100 text-green-700 border-green-300';
  };

  return (
    <main className="min-h-screen bg-slate-50 p-6 md:p-10 font-sans text-slate-800">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              SuRaksha AI - Family Protection Dashboard
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Live scam call logs and risk evaluations.
            </p>
          </div>
          <button
            onClick={fetchCalls}
            className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm rounded-xl transition-all shadow-sm active:scale-95 w-fit"
          >
            {loading ? 'Refreshing...' : 'Refresh Calls'}
          </button>
        </header>

        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/75 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <th className="py-4 px-6">Time</th>
                  <th className="py-4 px-6">Sender</th>
                  <th className="py-4 px-6">Risk Badge</th>
                  <th className="py-4 px-6">Confidence</th>
                  <th className="py-4 px-6">Reason / Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {calls.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-10 text-center text-slate-400">
                      {loading ? 'Loading call records...' : 'No call records logged yet.'}
                    </td>
                  </tr>
                ) : (
                  calls.map((call) => (
                    <tr key={call.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="py-4 px-6 text-slate-500 whitespace-nowrap text-xs">
                        {new Date(call.created_at).toLocaleString()}
                      </td>
                      <td className="py-4 px-6 font-medium text-slate-900 whitespace-nowrap">
                        {call.sender_number || 'Unknown'}
                      </td>
                      <td className="py-4 px-6 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${getBadgeClass(
                            call.risk
                          )}`}
                        >
                          {(call.risk || 'LOW').toUpperCase()}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-slate-600 whitespace-nowrap font-medium">
                        {call.confidence != null ? `${Math.round(call.confidence * 100)}%` : 'N/A'}
                      </td>
                      <td className="py-4 px-6 text-slate-600 max-w-md">
                        {call.reason || 'No explanation provided'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}