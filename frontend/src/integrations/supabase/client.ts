// Supabase replaced by our own FastAPI backend.
// This stub exists only so any remaining imports don't crash.
export const supabase = {
  from: () => ({
    select: async () => ({ data: [], error: null }),
    insert: async () => ({ data: null, error: null }),
    delete: () => ({ eq: async () => ({ error: null }) }),
  }),
  storage: {
    from: () => ({
      upload: async () => ({ error: null }),
      remove: async () => ({ error: null }),
    }),
  },
};
