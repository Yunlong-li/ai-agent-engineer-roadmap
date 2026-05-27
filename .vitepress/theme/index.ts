import DefaultTheme from 'vitepress/theme'
import { nextTick, watch } from 'vue'
import { inBrowser, useRoute } from 'vitepress'
import './style.css'

let mermaidInitialized = false

export default {
  extends: DefaultTheme,
  setup() {
    const route = useRoute()

    if (!inBrowser) return

    async function renderMermaid() {
      await nextTick()
      const mermaid = await import('mermaid')
      if (!mermaidInitialized) {
        mermaid.default.initialize({
          startOnLoad: false,
          theme: 'neutral',
          securityLevel: 'strict',
          flowchart: {
            htmlLabels: true,
            curve: 'basis'
          }
        })
        mermaidInitialized = true
      }

      const blocks = Array.from(document.querySelectorAll<HTMLElement>('div.language-mermaid'))

      for (const wrapper of blocks) {
        if (wrapper.dataset.mermaidRendered === 'true') continue

        const block = wrapper.querySelector('pre > code')
        if (!block) continue

        const graph = block.textContent ?? ''
        const container = document.createElement('div')
        container.className = 'mermaid vp-mermaid'
        container.textContent = graph
        wrapper.dataset.mermaidRendered = 'true'
        wrapper.replaceWith(container)
      }

      const diagrams = Array.from(document.querySelectorAll<HTMLElement>('.vp-mermaid:not([data-processed="true"])'))
      if (diagrams.length > 0) {
        await mermaid.default.run({ nodes: diagrams })
      }
    }

    watch(
      () => route.path,
      () => {
        renderMermaid()
      },
      { immediate: true }
    )
  }
}
