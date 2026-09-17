import { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import { GraphData } from '../types'

interface Props {
  data: GraphData
  onNodeClick?: (node: any) => void
  onEdgeClick?: (edge: any) => void
  height?: string
}

const typeColors: Record<string, string> = {
  Person: '#3b82f6',
  Phone: '#10b981',
  Vehicle: '#f59e0b',
  Location: '#ef4444',
  Organization: '#8b5cf6',
  FinancialAccount: '#06b6d4',
  Incident: '#ec4899',
  Document: '#6b7280',
  default: '#9ca3af'
}

export default function GraphViewer({
  data,
  onNodeClick,
  onEdgeClick,
  height = '600px'
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef = useRef<cytoscape.Core | null>(null)
  const [selectedNode, setSelectedNode] = useState<any>(null)

  useEffect(() => {
    if (!containerRef.current || !data.nodes.length) return

    /*
     * Important:
     * Spread properties FIRST, then set Cytoscape's reserved fields.
     *
     * Some backend properties may themselves contain fields such as
     * "id", "type", "source", or "target". If properties are spread
     * after these fields, they can overwrite the actual graph IDs and
     * cause Cytoscape to reject edges.
     */

    const elements = [
      ...data.nodes.map(node => ({
        data: {
          ...node.properties,
          id: node.id,
          label:
            node.label.length > 20
              ? node.label.substring(0, 20) + '...'
              : node.label,
          fullLabel: node.label,
          type: node.type
        }
      })),

      ...data.edges.map(edge => ({
        data: {
          ...edge.properties,
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.type,
          type: edge.type
        }
      }))
    ]

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele: any) =>
              typeColors[ele.data('type')] || typeColors.default,
            label: 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            color: '#fff',
            'text-outline-width': 2,
            'text-outline-color': (ele: any) =>
              typeColors[ele.data('type')] || typeColors.default,
            width: (ele: any) =>
              ele.data('type') === 'Person' ? 40 : 30,
            height: (ele: any) =>
              ele.data('type') === 'Person' ? 40 : 30,
            'border-width': 2,
            'border-color': '#fff'
          }
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#d1d5db',
            'target-arrow-color': '#d1d5db',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            label: 'data(label)',
            'font-size': '8px',
            color: '#6b7280',
            'text-rotation': 'autorotate'
          }
        },
        {
          selector: ':selected',
          style: {
            'border-width': 3,
            'border-color': '#3b82f6',
            'line-color': '#3b82f6',
            'target-arrow-color': '#3b82f6'
          }
        }
      ],
      layout: {
        name: 'cose',
        idealEdgeLength: 100,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 30,
        randomize: false,
        componentSpacing: 100,
        nodeRepulsion: 400000,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0
      } as any
    })

    cy.on('tap', 'node', (evt) => {
      const node = evt.target
      setSelectedNode(node.data())

      if (onNodeClick) {
        onNodeClick(node.data())
      }
    })

    cy.on('tap', 'edge', (evt) => {
      const edge = evt.target

      if (onEdgeClick) {
        onEdgeClick(edge.data())
      }
    })

    cyRef.current = cy

    return () => {
      cy.destroy()
      cyRef.current = null
    }
  }, [data, onNodeClick, onEdgeClick])

  const fitGraph = () => {
    if (cyRef.current) {
      cyRef.current.fit()
    }
  }

  const changeLayout = (layoutName: string) => {
    if (cyRef.current) {
      cyRef.current
        .layout({
          name: layoutName,
          fit: true,
          padding: 30
        } as any)
        .run()
    }
  }

  return (
    <div className="w-full">
      <div className="flex gap-2 mb-3">
        <button
          onClick={fitGraph}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
        >
          Fit
        </button>

        <button
          onClick={() => changeLayout('cose')}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
        >
          Cose
        </button>

        <button
          onClick={() => changeLayout('circle')}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
        >
          Circle
        </button>

        <button
          onClick={() => changeLayout('grid')}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
        >
          Grid
        </button>

        <button
          onClick={() => changeLayout('breadthfirst')}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
        >
          Tree
        </button>

        <div className="ml-auto flex gap-2 text-xs">
          {Object.entries(typeColors)
            .filter(([k]) => k !== 'default')
            .map(([type, color]) => (
              <div key={type} className="flex items-center gap-1">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: color }}
                />
                <span>{type}</span>
              </div>
            ))}
        </div>
      </div>

      <div
        ref={containerRef}
        style={{ height, width: '100%' }}
        className="border border-gray-200 rounded-lg bg-white"
      />

      {selectedNode && (
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
          <strong>Selected:</strong>{' '}
          {selectedNode.fullLabel || selectedNode.label} ({selectedNode.type})
        </div>
      )}
    </div>
  )
}
