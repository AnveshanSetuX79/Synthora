import { create } from 'zustand'

export const useDealsStore = create((set) => ({
  deals: [],
  selectedDeal: null,

  // Set deals
  setDeals: (deals) => set({ deals }),

  // Add deal
  addDeal: (deal) => set((state) => ({ deals: [...state.deals, deal] })),

  // Update deal
  updateDeal: (dealId, updates) =>
    set((state) => ({
      deals: state.deals.map((deal) =>
        deal.id === dealId ? { ...deal, ...updates } : deal
      ),
    })),

  // Select deal
  selectDeal: (deal) => set({ selectedDeal: deal }),

  // Clear selected deal
  clearSelectedDeal: () => set({ selectedDeal: null }),

  // Update milestone
  updateMilestone: (dealId, milestoneId, updates) =>
    set((state) => ({
      deals: state.deals.map((deal) =>
        deal.id === dealId
          ? {
              ...deal,
              milestones: deal.milestones.map((milestone) =>
                milestone.id === milestoneId
                  ? { ...milestone, ...updates }
                  : milestone
              ),
            }
          : deal
      ),
    })),
}))
