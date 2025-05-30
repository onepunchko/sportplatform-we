/**
 * 简易Markdown解析器
 * 支持基本markdown格式，如标题、列表、表格、引用等
 */

/**
 * 将Markdown文本转换为微信小程序可以显示的富文本节点
 * @param {String} markdown Markdown文本
 * @returns {Array} 转换后的富文本节点数组
 */
function parseMarkdown(markdown) {
  if (!markdown) return [];
  
  // 分割成段落
  const paragraphs = markdown.split('\n\n');
  const nodes = [];
  
  paragraphs.forEach(paragraph => {
    // 移除前后空白
    paragraph = paragraph.trim();
    if (!paragraph) return;
    
    // 解析标题
    if (paragraph.startsWith('# ')) {
      nodes.push(parseHeading(paragraph, 1));
    } else if (paragraph.startsWith('## ')) {
      nodes.push(parseHeading(paragraph, 2));
    } else if (paragraph.startsWith('### ')) {
      nodes.push(parseHeading(paragraph, 3));
    } else if (paragraph.startsWith('#### ')) {
      nodes.push(parseHeading(paragraph, 4));
    } else if (paragraph.startsWith('##### ')) {
      nodes.push(parseHeading(paragraph, 5));
    } else if (paragraph.startsWith('###### ')) {
      nodes.push(parseHeading(paragraph, 6));
    } 
    // 解析表格
    else if (paragraph.includes('|') && paragraph.includes('\n') && paragraph.includes('-')) {
      const tableNodes = parseTable(paragraph);
      nodes.push(...tableNodes);
    }
    // 解析列表
    else if (paragraph.match(/^[\s]*[*\-+][\s]/m)) {
      nodes.push(parseUnorderedList(paragraph));
    }
    // 解析有序列表
    else if (paragraph.match(/^[\s]*\d+\.[\s]/m)) {
      nodes.push(parseOrderedList(paragraph));
    }
    // 解析引用
    else if (paragraph.startsWith('> ')) {
      nodes.push(parseBlockquote(paragraph));
    }
    // 普通段落
    else {
      nodes.push(parseParagraph(paragraph));
    }
  });
  
  return nodes;
}

/**
 * 解析行内格式
 * @param {String} text 文本内容
 * @returns {String} 添加了行内样式的富文本
 */
function parseInline(text) {
  // 加粗 **text** 或 __text__
  text = text.replace(/(\*\*|__)(.*?)\1/g, '<strong>$2</strong>');
  
  // 斜体 *text* 或 _text_
  text = text.replace(/(\*|_)(.*?)\1/g, '<em>$2</em>');
  
  // 行内代码 `code`
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // 链接 [text](url)
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  
  return text;
}

/**
 * 解析标题
 * @param {String} text 标题文本
 * @param {Number} level 标题级别 1-6
 * @returns {Object} 富文本节点
 */
function parseHeading(text, level) {
  const content = text.slice(level + 1); // 移除 # 和空格
  return {
    name: 'h' + level,
    attrs: {
      class: 'md-h' + level
    },
    children: [{
      type: 'text',
      text: parseInline(content)
    }]
  };
}

/**
 * 解析普通段落
 * @param {String} text 段落文本
 * @returns {Object} 富文本节点
 */
function parseParagraph(text) {
  return {
    name: 'p',
    attrs: {
      class: 'md-p'
    },
    children: [{
      type: 'text',
      text: parseInline(text)
    }]
  };
}

/**
 * 解析无序列表
 * @param {String} text 列表文本
 * @returns {Object} 富文本节点
 */
function parseUnorderedList(text) {
  const items = text.split('\n')
    .map(line => line.trim())
    .filter(line => line.match(/^[*\-+][\s]/))
    .map(line => {
      return {
        name: 'li',
        attrs: {
          class: 'md-li'
        },
        children: [{
          type: 'text',
          text: parseInline(line.slice(1).trim()) // 移除 * 和空格
        }]
      };
    });
  
  return {
    name: 'ul',
    attrs: {
      class: 'md-ul'
    },
    children: items
  };
}

/**
 * 解析有序列表
 * @param {String} text 列表文本
 * @returns {Object} 富文本节点
 */
function parseOrderedList(text) {
  const items = text.split('\n')
    .map(line => line.trim())
    .filter(line => line.match(/^\d+\.[\s]/))
    .map(line => {
      return {
        name: 'li',
        attrs: {
          class: 'md-li'
        },
        children: [{
          type: 'text',
          text: parseInline(line.replace(/^\d+\.[\s]/, '')) // 移除数字和点
        }]
      };
    });
  
  return {
    name: 'ol',
    attrs: {
      class: 'md-ol'
    },
    children: items
  };
}

/**
 * 解析引用块
 * @param {String} text 引用文本
 * @returns {Object} 富文本节点
 */
function parseBlockquote(text) {
  // 移除每行开头的 >
  const content = text.split('\n')
    .map(line => line.replace(/^>[\s]?/, '').trim())
    .join('\n');
  
  return {
    name: 'blockquote',
    attrs: {
      class: 'md-blockquote'
    },
    children: [{
      type: 'text',
      text: parseInline(content)
    }]
  };
}

/**
 * 解析表格
 * @param {String} text 表格文本
 * @returns {Array} 富文本节点数组
 */
function parseTable(text) {
  const lines = text.trim().split('\n');
  
  // 检查是否是有效表格
  if (lines.length < 3) return [parseParagraph(text)];
  
  // 解析表头
  const headerLine = lines[0];
  const separatorLine = lines[1];
  
  // 验证分隔符行
  if (!separatorLine.includes('|') || !separatorLine.includes('-')) {
    return [parseParagraph(text)];
  }
  
  // 解析列
  const columns = headerLine.split('|')
    .map(col => col.trim())
    .filter(col => col.length > 0);
  
  // 解析对齐方式
  const alignments = separatorLine.split('|')
    .map(col => col.trim())
    .filter(col => col.length > 0)
    .map(col => {
      if (col.startsWith(':') && col.endsWith(':')) return 'center';
      if (col.endsWith(':')) return 'right';
      return 'left';
    });
  
  // 创建表头
  const thead = {
    name: 'thead',
    children: [
      {
        name: 'tr',
        children: columns.map((col, index) => {
          return {
            name: 'th',
            attrs: {
              class: `md-th md-align-${alignments[index] || 'left'}`
            },
            children: [{ type: 'text', text: parseInline(col) }]
          };
        })
      }
    ]
  };
  
  // 创建表体
  const tbody = {
    name: 'tbody',
    children: []
  };
  
  // 处理数据行
  for (let i = 2; i < lines.length; i++) {
    const dataLine = lines[i];
    const cells = dataLine.split('|')
      .map(cell => cell.trim())
      .filter((cell, index) => index < columns.length);
    
    const tr = {
      name: 'tr',
      children: cells.map((cell, index) => {
        return {
          name: 'td',
          attrs: {
            class: `md-td md-align-${alignments[index] || 'left'}`
          },
          children: [{ type: 'text', text: parseInline(cell) }]
        };
      })
    };
    
    tbody.children.push(tr);
  }
  
  return [
    {
      name: 'div',
      attrs: { class: 'md-table-container' },
      children: [
        {
          name: 'table',
          attrs: { class: 'md-table' },
          children: [thead, tbody]
        }
      ]
    }
  ];
}

/**
 * 将Markdown文本转换为适合在小程序中显示的HTML
 * @param {String} markdown Markdown文本 
 * @returns {String} HTML字符串
 */
function markdownToHtml(markdown) {
  if (!markdown) return '';
  
  // 处理标题
  let html = markdown
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>');
  
  // 处理粗体和斜体
  html = html
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    .replace(/_(.*?)_/g, '<em>$1</em>');
  
  // 处理行内代码
  html = html.replace(/`(.*?)`/g, '<code>$1</code>');
  
  // 处理链接
  html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');
  
  // 处理表格 - 支持多个表格
  html = processAllTables(html);
  
  // 处理无序列表和有序列表
  html = processAllLists(html);
  
  // 处理段落
  html = html.replace(/^(?!<[^>]*>|[\s]*[*\-+][\s])(.*)/gm, '<p>$1</p>');
  
  return html;
}

/**
 * 处理所有无序列表和有序列表
 * @param {String} html Markdown HTML文本
 * @returns {String} 处理后的HTML
 */
function processAllLists(html) {
  // 分割为行
  const lines = html.split('\n');
  let result = [];
  let listItems = [];
  let inList = false;
  let isOrderedList = false;
  
  // 处理每一行
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // 检测无序列表项
    const isUnorderedItem = line.match(/^[\s]*[*\-+][\s]/);
    // 检测有序列表项
    const isOrderedItem = line.match(/^[\s]*\d+\.[\s]/);
    
    if (isUnorderedItem || isOrderedItem) {
      // 如果类型变化了，先处理前一个列表
      const currentIsOrdered = isOrderedItem ? true : false;
      if (inList && isOrderedList !== currentIsOrdered && listItems.length > 0) {
        const listHtml = convertListToHtml(listItems, isOrderedList);
        result.push(listHtml);
        listItems = [];
      }
      
      isOrderedList = currentIsOrdered;
      inList = true;
      
      // 提取列表项内容
      let itemContent;
      if (isOrderedItem) {
        itemContent = line.replace(/^[\s]*\d+\.[\s]/, '');
      } else {
        itemContent = line.replace(/^[\s]*[*\-+][\s]/, '');
      }
      
      listItems.push(parseInline(itemContent));
    } else {
      // 结束当前列表
      if (inList) {
        const listHtml = convertListToHtml(listItems, isOrderedList);
        result.push(listHtml);
        listItems = [];
        inList = false;
      }
      
      // 添加非列表行
      result.push(lines[i]);
    }
  }
  
  // 处理文档末尾的列表
  if (inList && listItems.length > 0) {
    const listHtml = convertListToHtml(listItems, isOrderedList);
    result.push(listHtml);
  }
  
  return result.join('\n');
}

/**
 * 将列表项数组转换为HTML列表
 * @param {Array} listItems 列表项内容数组
 * @param {Boolean} isOrdered 是否为有序列表
 * @returns {String} HTML列表
 */
function convertListToHtml(listItems, isOrdered = false) {
  if (listItems.length === 0) return '';
  
  const listTag = isOrdered ? 'ol' : 'ul';
  const listClass = isOrdered ? 'md-ol' : 'md-ul';
  
  let listHtml = `<${listTag} class="${listClass}">`;
  
  listItems.forEach(item => {
    listHtml += `<li class="md-li">${item}</li>`;
  });
  
  listHtml += `</${listTag}>`;
  return listHtml;
}

/**
 * 处理Markdown文本中的所有表格
 * @param {String} html Markdown HTML文本
 * @returns {String} 处理后的HTML
 */
function processAllTables(html) {
  // 检查是否有表格
  if (!html.includes('|') || !html.includes('\n') || !html.includes('-')) {
    return html;
  }
  
  // 分割文本为行
  const lines = html.split('\n');
  let result = [];
  let tableLines = [];
  let inTable = false;
  
  // 逐行处理文本，识别和处理表格
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // 检测表格的开始 (包含 | 和内容)
    if (!inTable && line.includes('|') && line.trim() !== '') {
      // 检查下一行是否是分隔行
      if (i + 1 < lines.length && lines[i + 1].includes('|') && lines[i + 1].includes('-')) {
        inTable = true;
        tableLines = [line];
        continue;
      }
    }
    
    // 已经在表格内，继续收集表格行
    if (inTable) {
      tableLines.push(line);
      
      // 检测表格的结束 (下一行不包含 | 或者是空行)
      if (i + 1 >= lines.length || !lines[i + 1].includes('|') || lines[i + 1].trim() === '') {
        // 将收集到的表格行转换为HTML表格
        const tableHtml = convertTableToHtml(tableLines);
        result.push(tableHtml);
        inTable = false;
        tableLines = [];
      }
    } else {
      // 不在表格内，直接添加行
      result.push(lines[i]);
    }
  }
  
  return result.join('\n');
}

/**
 * 将表格行转换为HTML表格
 * @param {Array} tableLines 表格行数组
 * @returns {String} HTML表格
 */
function convertTableToHtml(tableLines) {
  if (tableLines.length < 2) return tableLines.join('\n');
  
  let tableHtml = '<div class="md-table-container"><table class="md-table">';
  
  // 处理表头
  const headerLine = tableLines[0];
  const separatorLine = tableLines[1];
  
  // 验证分隔符行
  if (!separatorLine.includes('-')) {
    return tableLines.join('\n');
  }
  
  // 解析表头单元格
  const headerCells = headerLine.split('|')
    .map(cell => cell.trim())
    .filter(cell => cell !== '');
  
  // 生成表头HTML
  tableHtml += '<thead><tr>';
  headerCells.forEach(cell => {
    // 处理表头内的行内格式
    tableHtml += `<th>${parseInline(cell)}</th>`;
  });
  tableHtml += '</tr></thead><tbody>';
  
  // 处理表格数据行
  for (let i = 2; i < tableLines.length; i++) {
    const dataLine = tableLines[i];
    if (!dataLine.includes('|')) continue;
    
    const dataCells = dataLine.split('|')
      .map(cell => cell.trim())
      .filter(cell => cell !== '');
    
    if (dataCells.length === 0) continue;
    
    tableHtml += '<tr>';
    dataCells.forEach((cell, index) => {
      if (index < headerCells.length) {
        // 处理单元格内的行内格式
        tableHtml += `<td>${parseInline(cell)}</td>`;
      }
    });
    tableHtml += '</tr>';
  }
  
  tableHtml += '</tbody></table></div>';
  
  return tableHtml;
}

module.exports = {
  parseMarkdown,
  markdownToHtml
}; 