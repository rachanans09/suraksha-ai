import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://nxcqtyvnjufduwidudwo.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im54Y3F0eXZuanVmZHV3aWR1ZHdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODcyMTYzMDAsImV4cCI6MjEwMjc5MjMwMH0.3xAEW_PJmh4mlgneUmph_M20e3xr2OAw8OJZ5CN5S0c';

let supabaseInstance: SupabaseClient | null = null;

export const getSupabase = (): SupabaseClient => {
  if (!supabaseInstance) {
    supabaseInstance = createClient(supabaseUrl, supabaseAnonKey);
  }
  return supabaseInstance;
};