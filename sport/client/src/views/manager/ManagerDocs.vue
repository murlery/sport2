<template>
    <section class="card docs">
        <div class="card-header">
            <div>
                
                <h2>Формирование документов</h2>
            </div>
        </div>

        <div class="form-grid">
            <label class="field">
                <span>Тип документа</span>
                <select v-model="docForm.doc_type">
                    <option v-for="t in docTypes" :key="t" :value="t">{{ t }}</option>
                </select>
            </label>
        </div>

        <label class="field full">
            <span>Содержание документа</span>
            <textarea rows="8" v-model="docForm.content"
                placeholder="Введите содержание документа"></textarea>
        </label>

        <div class="actions end">
            <button class="btn ghost" @click="resetDocForm">Очистить</button>
            <button class="btn primary" :disabled="loadingDoc" @click="generateDoc">
                {{ loadingDoc ? 'Генерируем...' : 'Сгенерировать и скачать' }}
            </button>
        </div>

        <!-- Список последних документов -->
        <div v-if="recentDocs.length > 0" class="recent-docs">
            <h3>Последние документы</h3>
            <div class="docs-list">
                <div v-for="doc in recentDocs" :key="doc.id" class="doc-item">
                    <span class="doc-type">{{ doc.doc_type }}</span>
                    <span class="doc-date">{{ formatDate(doc.created_at) }}</span>
                    <button class="btn-icon" @click="downloadDoc(doc)" title="Скачать">
                        📥
                    </button>
                </div>
            </div>
        </div>

        <!-- Сообщение об ошибке -->
        <div v-if="error" class="error-message">
            {{ error }}
        </div>
    </section>
</template>

<script>
import axios from '../../axios'

export default {
    name: 'ManagerDocs',
    data() {
        return {
            docForm: { 
                doc_type: 'Приказ', 
                content: ''
            },
            docTypes: ['Приказ', 'Акт', 'Справка', 'Протокол', 'Пояснительная записка'],
            loadingDoc: false,
            recentDocs: [],
            error: null
        }
    },
    
    async mounted() {
        await this.loadRecentDocs()
    },
    
    methods: {
        async loadRecentDocs() {
            try {
                const response = await axios.get('/api/admin-docs/')
                this.recentDocs = response.data.slice(0, 5) // Последние 5 документов
            } catch (error) {
                console.error('Ошибка загрузки документов:', error)
            }
        },
        
        async generateDoc() {
            // Валидация
            if (!this.docForm.doc_type || !this.docForm.content) {
                this.error = 'Заполните все поля'
                return
            }
            
            this.loadingDoc = true
            this.error = null
            
            try {
                // Формируем красивый текст документа
                const content = this.composeDocText()
                const fileName = `${this.docForm.doc_type}_${this.getCurrentDate()}.txt`
                
                // Создаем файл из текста
                const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
                const file = new File([blob], fileName, { type: 'text/plain' })
                
                // Создаем FormData для отправки
                const formData = new FormData()
                formData.append('doc_type', this.docForm.doc_type)
                formData.append('file_path', file) // Поле file_path для загрузки файла

                console.log('Отправка документа:', {
                    doc_type: this.docForm.doc_type,
                    fileName: fileName
                })

                // Отправляем запрос
                await axios.post('/api/admin-docs/', formData, {
                    headers: { 
                        'Content-Type': 'multipart/form-data'
                    }
                })
                
                // Скачиваем файл локально
                this.downloadBlob(blob, fileName)
                
                // Обновляем список последних документов
                await this.loadRecentDocs()
                
                // Очищаем форму
                this.resetDocForm()
                
            } catch (error) {
                console.error('Ошибка генерации документа:', error)
                
                if (error.response) {
                    console.error('Детали ошибки:', error.response.data)
                    this.error = `Ошибка сервера: ${JSON.stringify(error.response.data)}`
                } else if (error.request) {
                    this.error = 'Сервер не отвечает. Проверьте подключение.'
                } else {
                    this.error = 'Ошибка при отправке запроса'
                }
            } finally {
                this.loadingDoc = false
            }
        },
        
        composeDocText() {
            const date = new Date().toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            })
            
            return [
                `ТИП ДОКУМЕНТА: ${this.docForm.doc_type}`,
                `ДАТА СОЗДАНИЯ: ${date}`,
                '',
                this.docForm.content,
                '',
                `---`,
                `Документ сгенерирован автоматически системой SportSchool`,
            ].join('\n')
        },
        
        getCurrentDate() {
            const d = new Date()
            const year = d.getFullYear()
            const month = String(d.getMonth() + 1).padStart(2, '0')
            const day = String(d.getDate()).padStart(2, '0')
            return `${year}-${month}-${day}`
        },
        
        formatDate(dateString) {
            if (!dateString) return '—'
            const d = new Date(dateString)
            return d.toLocaleDateString('ru-RU')
        },
        
        downloadBlob(blob, filename) {
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = filename
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            window.URL.revokeObjectURL(url)
        },
        
        async downloadDoc(doc) {
            if (!doc.file_path) {
                this.error = 'Файл не найден'
                return
            }
            
            try {
                const response = await axios.get(doc.file_path, {
                    responseType: 'blob'
                })
                
                // Получаем имя файла из URL
                const fileName = doc.file_path.split('/').pop()
                
                this.downloadBlob(response.data, fileName)
            } catch (error) {
                console.error('Ошибка скачивания:', error)
                this.error = 'Не удалось скачать документ'
            }
        },
        
        resetDocForm() {
            this.docForm = { 
                doc_type: 'Приказ', 
                content: '' 
            }
            this.error = null
        }
    }
}
</script>

<style scoped>
.card {
    background: #fff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    margin: 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.eyebrow {
    font-size: 12px;
    color: #6b7280;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

h2 {
    margin: 4px 0 0;
    font-size: 18px;
    color: #1f2937;
}

.form-grid {
    margin-bottom: 16px;
}

.field {
    display: flex;
    flex-direction: column;
    font-size: 14px;
    margin-bottom: 16px;
}

.field.full {
    width: 100%;
}

.field span {
    margin-bottom: 6px;
    font-weight: 600;
    color: #4b5563;
}

.field select,
.field input,
.field textarea {
    padding: 10px 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    outline: none;
    transition: all 0.2s;
}

.field select:focus,
.field input:focus,
.field textarea:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 40px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn.ghost {
    background: white;
    border: 1px solid #d1d5db;
    color: #4b5563;
}

.btn.primary {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.btn-icon {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    border-radius: 50%;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.btn-icon:hover {
    background: #f3f4f6;
}

.recent-docs {
    margin-top: 30px;
    border-top: 1px solid #e5e7eb;
    padding-top: 20px;
}

.recent-docs h3 {
    margin: 0 0 12px;
    font-size: 16px;
    color: #374151;
}

.docs-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.doc-item {
    display: flex;
    align-items: center;
    padding: 10px;
    background: #f9fafb;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}

.doc-type {
    font-weight: 600;
    color: #1f2937;
    flex: 2;
}

.doc-date {
    color: #6b7280;
    font-size: 13px;
    flex: 1;
}

.error-message {
    margin-top: 16px;
    padding: 12px;
    background: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    color: #991b1b;
    font-size: 14px;
}

.muted {
    color: #6b7280;
}

.small {
    font-size: 12px;
}
</style>