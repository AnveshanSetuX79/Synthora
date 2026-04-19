import { create } from 'zustand'

export const useLeadsStore = create((set) => ({
  leads: [],
  selectedLead: null,
  filters: {
    category: null,
    scoreMin: null,
    scoreMax: null,
    freshness: null,
    status: null,
  },

  // Set leads
  setLeads: (leads) => set({ leads }),

  // Add lead
  addLead: (lead) => set((state) => ({ leads: [...state.leads, lead] })),

  // Update lead
  updateLead: (leadId, updates) =>
    set((state) => ({
      leads: state.leads.map((lead) =>
        lead.id === leadId ? { ...lead, ...updates } : lead
      ),
    })),

  // Remove lead
  removeLead: (leadId) =>
    set((state) => ({
      leads: state.leads.filter((lead) => lead.id !== leadId),
    })),

  // Select lead
  selectLead: (lead) => set({ selectedLead: lead }),

  // Clear selected lead
  clearSelectedLead: () => set({ selectedLead: null }),

  // Update filters
  updateFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),

  // Clear filters
  clearFilters: () =>
    set({
      filters: {
        category: null,
        scoreMin: null,
        scoreMax: null,
        freshness: null,
        status: null,
      },
    }),
}))
