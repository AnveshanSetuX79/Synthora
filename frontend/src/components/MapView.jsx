import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import MarkerClusterGroup from 'react-leaflet-cluster'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Custom marker icon based on opportunity tag and freshness
const createCustomIcon = (opportunityTag, freshness) => {
  const colors = {
    High: '#ef4444', // red
    Medium: '#f59e0b', // orange
    Low: '#10b981', // green
  }
  
  const color = colors[opportunityTag] || colors.Low
  const freshnessEmoji = freshness === 'high' ? '🔥' : freshness === 'medium' ? '⚡' : ''
  
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background: ${color};
        border: 3px solid white;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        position: relative;
      ">
        ${freshnessEmoji}
        ${!freshnessEmoji ? '<div style="width: 12px; height: 12px; background: white; border-radius: 50%;"></div>' : ''}
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  })
}

// Component to handle map center updates
function MapUpdater({ center, zoom }) {
  const map = useMap()
  
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom())
    }
  }, [center, zoom, map])
  
  // Force map to recalculate size on mount and when container changes
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize()
    }, 100)
    return () => clearTimeout(timer)
  }, [map])
  
  return null
}

function MapView({ leads, onLeadSelect, onLeadClick, selectedLeadId, userLocation, center, zoom = 13, className = '' }) {
  // Default center (Pune, India)
  const defaultCenter = [18.5204, 73.8567]
  const mapCenter = center || (userLocation ? [userLocation.lat, userLocation.lng] : defaultCenter)
  
  // Filter leads with valid coordinates
  // Handle both flat structure (AvailableLeadItem) and nested structure (LeadResponse)
  const validLeads = leads.filter(
    lead => (lead.latitude && lead.longitude) || (lead.business?.latitude && lead.business?.longitude)
  )
  
  // Debug: Log the first lead to see its structure
  if (leads.length > 0) {
    console.log('First lead structure:', leads[0])
    console.log('Valid leads count:', validLeads.length)
  }
  
  if (validLeads.length === 0) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 rounded-lg ${className}`}>
        <div className="text-center p-8">
          <p className="text-gray-600 mb-2">No leads with location data available</p>
          <p className="text-sm text-gray-500">
            Discover new leads to see them on the map
          </p>
        </div>
      </div>
    )
  }
  
  return (
    <div className={`${className}`} style={{ height: '600px', width: '100%' }}>
      <MapContainer
        center={mapCenter}
        zoom={zoom}
        style={{ height: '100%', width: '100%', borderRadius: '0.5rem' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapUpdater center={mapCenter} zoom={zoom} />
        
        <MarkerClusterGroup
          chunkedLoading
          maxClusterRadius={50}
          spiderfyOnMaxZoom={true}
          showCoverageOnHover={false}
        >
          {validLeads.map((lead) => {
            // Handle both flat structure (AvailableLeadItem) and nested structure (LeadResponse)
            const latitude = lead.latitude || lead.business?.latitude
            const longitude = lead.longitude || lead.business?.longitude
            const businessName = lead.business_name || lead.business?.name
            const category = lead.category || lead.business?.category
            const address = lead.address || lead.business?.address
            const opportunityTag = lead.opportunity_tag || lead.insights?.opportunity_tag || 'Low'
            const freshness = lead.freshness || lead.insights?.freshness || 'low'
            const leadId = lead.lead_id || lead.id
            
            // Use onLeadSelect if provided, otherwise onLeadClick
            const handleLeadClick = onLeadSelect || onLeadClick
            
            return (
              <Marker
                key={leadId}
                position={[latitude, longitude]}
                icon={createCustomIcon(opportunityTag, freshness)}
                eventHandlers={{
                  click: () => handleLeadClick && handleLeadClick(lead)
                }}
              >
                <Popup>
                  <div className="p-2 min-w-[200px]">
                    <h3 className="font-bold text-lg mb-1">{businessName}</h3>
                    <p className="text-sm text-gray-600 mb-2">{category}</p>
                    <p className="text-xs text-gray-500 mb-2">{address}</p>
                    
                    <div className="flex gap-2 mb-2">
                      <span className={`px-2 py-1 text-xs rounded ${
                        opportunityTag === 'High' ? 'bg-red-100 text-red-800' :
                        opportunityTag === 'Medium' ? 'bg-orange-100 text-orange-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {opportunityTag}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded ${
                        freshness === 'high' ? 'bg-green-100 text-green-800' :
                        freshness === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {freshness}
                      </span>
                    </div>
                    
                    <div className="text-sm mb-2">
                      <strong>Score:</strong> {lead.digital_score || lead.insights?.digital_score || 0}/100
                    </div>
                    
                    <button
                      onClick={() => handleLeadClick && handleLeadClick(lead)}
                      className="w-full bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                    >
                      View Details
                    </button>
                  </div>
                </Popup>
              </Marker>
            )
          })}
        </MarkerClusterGroup>
      </MapContainer>
      
      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white p-3 rounded-lg shadow-lg z-[1000]">
        <h4 className="font-bold text-sm mb-2">Legend</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span>High Opportunity</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-orange-500"></div>
            <span>Medium Opportunity</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>Low Opportunity</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🔥</span>
            <span>Fresh (&lt; 7 days)</span>
          </div>
          <div className="flex items-center gap-2">
            <span>⚡</span>
            <span>Medium (7-30 days)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MapView
