import DefaultTheme from 'vitepress/theme'
import { nextTick, watch } from 'vue'
import { inBrowser, useRoute } from 'vitepress'
import './style.css'

export default {
  extends: DefaultTheme,
  setup() {
    const route = useRoute()

    if (!inBrowser) return

    async function renderMermaid() {
      await nextTick()
      const mermaid = await import('mermaid')
      mermaid.default.initialize({
        startOnLoad: false,
        theme: 'neutral',
        securityLevel: 'strict',
        flowchart: {
          htmlLabels: true,
          curve: 'basis'
        }
      })

      const blocks = Array.from(document.querySelectorAll('pre > code.language-mermaid'))

      for (const block of blocks) {
        const pre = block.parentElement
        if (!pre || pre.dataset.mermaidRendered === 'true') continue

        const graph = block.textContent ?? ''
        const container = document.createElement('div')
        container.className = 'mermaid vp-mermaid'
        container.textContent = graph
        pre.replaceWith(container)
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
