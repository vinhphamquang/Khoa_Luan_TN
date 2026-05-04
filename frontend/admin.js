// ---- ADMIN LOGIC ----
document.addEventListener('DOMContentLoaded', () => {
    console.log("Admin page loaded!");
    const loggedUser = JSON.parse(localStorage.getItem('smartfood_user'));
    
    // Redirect if not admin
    if (!loggedUser || loggedUser.role !== 'admin') {
        window.location.href = '/';
        return;
    }

    // --- Navbar Setup ---
    // Show user name
    const displayUsername = document.getElementById('display-username');
    if (displayUsername) displayUsername.textContent = loggedUser.name;

    // Show nutrition link (visible for logged-in users)
    const nutritionLink = document.getElementById('nav-nutrition-link');
    if (nutritionLink) nutritionLink.style.display = '';

    // Mobile nav toggle
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }

    // Logout logic
    const btnLogout = document.getElementById('btn-admin-logout');
    if (btnLogout) {
        btnLogout.addEventListener('click', () => {
            localStorage.removeItem('smartfood_user');
            window.location.href = '/';
        });
    }

    // Init animations
    const reveals = document.querySelectorAll('.reveal');
    setTimeout(() => {
        reveals.forEach(el => el.classList.add('visible'));
    }, 100);

    // ============================================
    // BULK SELECT STATE
    // ============================================
    let selectedFoodIds = new Set();

    function updateBulkUI() {
        const bar = document.getElementById('bulk-action-bar');
        const countEl = document.getElementById('bulk-count');
        const listEl = document.getElementById('bulk-selected-list');
        const count = selectedFoodIds.size;
        
        if (count > 0) {
            bar.classList.remove('hidden');
            countEl.textContent = `${count} món đã chọn`;

            // Build tags showing selected food names
            let tagsHtml = '';
            document.querySelectorAll('#tb-foods tr').forEach(row => {
                const id = parseInt(row.dataset.foodId);
                if (selectedFoodIds.has(id)) {
                    const name = row.querySelectorAll('td')[1]?.textContent || '';
                    tagsHtml += `<span class="bulk-tag" data-id="${id}">
                        <strong>#${id}</strong> ${name}
                        <i class="fa-solid fa-xmark bulk-tag-remove" onclick="window._removeBulkItem(${id})"></i>
                    </span>`;
                }
            });
            listEl.innerHTML = tagsHtml;
        } else {
            bar.classList.add('hidden');
            listEl.innerHTML = '';
        }

        // Sync select-all checkbox in bulk bar
        const allCheckboxes = document.querySelectorAll('.food-row-checkbox');
        const bulkSelectAll = document.getElementById('bulk-select-all');
        const allChecked = allCheckboxes.length > 0 && selectedFoodIds.size === allCheckboxes.length;
        if (bulkSelectAll) bulkSelectAll.checked = allChecked;

        // Highlight rows
        document.querySelectorAll('#tb-foods tr').forEach(row => {
            const id = parseInt(row.dataset.foodId);
            if (selectedFoodIds.has(id)) {
                row.classList.add('row-selected');
            } else {
                row.classList.remove('row-selected');
            }
        });
    }

    // Remove single item from bulk selection
    window._removeBulkItem = function(id) {
        selectedFoodIds.delete(id);
        const cb = document.querySelector(`.food-row-checkbox[data-food-id="${id}"]`);
        if (cb) cb.checked = false;
        updateBulkUI();
    };

    function toggleFoodSelect(id, checked) {
        if (checked) selectedFoodIds.add(id);
        else selectedFoodIds.delete(id);
        updateBulkUI();
    }

    function toggleSelectAll(checked) {
        const allCheckboxes = document.querySelectorAll('.food-row-checkbox');
        allCheckboxes.forEach(cb => {
            cb.checked = checked;
            const id = parseInt(cb.dataset.foodId);
            if (checked) selectedFoodIds.add(id);
            else selectedFoodIds.delete(id);
        });
        updateBulkUI();
    }

    // Select-all from bulk bar
    document.getElementById('bulk-select-all')?.addEventListener('change', (e) => {
        toggleSelectAll(e.target.checked);
    });
    // Cancel bulk selection
    document.getElementById('btn-bulk-cancel')?.addEventListener('click', () => {
        toggleSelectAll(false);
    });

    // Bulk Soft Delete
    document.getElementById('btn-bulk-soft-delete')?.addEventListener('click', async () => {
        const ids = Array.from(selectedFoodIds);
        if (ids.length === 0) return;
        if (!confirm(`Bạn có chắc muốn KHÓA (soft delete) ${ids.length} món ăn đã chọn?`)) return;

        let success = 0, fail = 0;
        for (const id of ids) {
            try {
                const res = await fetch(`/api/admin/foods/${id}`, { method: 'DELETE' });
                const r = await res.json();
                if (r.success) success++;
                else fail++;
            } catch { fail++; }
        }
        alert(`Đã khóa ${success} món.${fail > 0 ? ` Lỗi: ${fail} món.` : ''}`);
        selectedFoodIds.clear();
        updateBulkUI();
        fetchAdminFoods();
    });

    // Bulk Hard Delete
    document.getElementById('btn-bulk-hard-delete')?.addEventListener('click', async () => {
        const ids = Array.from(selectedFoodIds);
        if (ids.length === 0) return;
        if (!confirm(`⚠️ BẠN CÓ CHẮC MUỐN XÓA VĨNH VIỄN ${ids.length} MÓN ĂN?\n\nHành động này KHÔNG THỂ HOÀN TÁC!`)) return;
        if (!confirm(`Xác nhận lần cuối: XÓA VĨNH VIỄN ${ids.length} món ăn đã chọn?`)) return;

        let success = 0, fail = 0;
        for (const id of ids) {
            try {
                const res = await fetch(`/api/admin/foods/${id}/hard-delete`, { method: 'DELETE' });
                const r = await res.json();
                if (r.success) success++;
                else fail++;
            } catch { fail++; }
        }
        alert(`✅ Đã xóa vĩnh viễn ${success} món.${fail > 0 ? ` Lỗi: ${fail} món.` : ''}`);
        selectedFoodIds.clear();
        updateBulkUI();
        fetchAdminFoods();
    });

    // Tabs logic
    const tabs = document.querySelectorAll('.admin-tab');
    const contents = document.querySelectorAll('.admin-tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.add('hidden'));
            
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.remove('hidden');
            
            // Refresh data if needed based on tab activated
            if(tab.dataset.tab === 'admin-stats') fetchAdminStats();
            if(tab.dataset.tab === 'admin-foods') fetchAdminFoods();
            if(tab.dataset.tab === 'admin-users') fetchAdminUsers();
            if(tab.dataset.tab === 'admin-history') fetchAdminHistory();
        });
    });

    // Food Modal Logic
    const btnAddFood = document.getElementById('btn-admin-add-food');
    const adminModalOverlay = document.getElementById('admin-modal-overlay');
    const foodForm = document.getElementById('food-admin-form');
    const btnAddIng = document.getElementById('fa-add-ing');
    const ingsContainer = document.getElementById('fa-ingredients');

    if (btnAddFood) {
        btnAddFood.addEventListener('click', () => {
            foodForm.reset();
            document.getElementById('fa-id').value = '';
            document.getElementById('food-modal-title').textContent = 'Thêm Món Ăn';
            ingsContainer.innerHTML = ''; // clear ingredients
            addIngredientRow('');
            adminModalOverlay.classList.remove('hidden');
        });
    }

    if (btnAddIng) {
        btnAddIng.addEventListener('click', () => {
            addIngredientRow('');
        });
    }

    // Excel Upload Logic
    const btnUploadExcel = document.getElementById('btn-upload-excel');
    const uploadExcelInput = document.getElementById('fa-upload-excel');

    if (btnUploadExcel && uploadExcelInput) {
        btnUploadExcel.addEventListener('click', () => {
            uploadExcelInput.click();
        });

        uploadExcelInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, {type: 'array'});
                    
                    const firstSheetName = workbook.SheetNames[0];
                    const worksheet = workbook.Sheets[firstSheetName];
                    
                    const json = XLSX.utils.sheet_to_json(worksheet, {header: 1});
                    
                    let startIndex = 0;
                    if (json.length > 0 && typeof json[0][0] === 'string' && json[0][0].toLowerCase().includes('tên')) {
                        startIndex = 1; // Bỏ qua header
                    }
                    
                    // Nếu chỉ có 1 dòng rỗng mặc định thì xóa đi trước khi thêm từ Excel
                    const currentRows = ingsContainer.querySelectorAll('div');
                    if (currentRows.length === 1) {
                        const nameInput = currentRows[0].querySelector('.ing-name');
                        const qtyInput = currentRows[0].querySelector('.ing-qty');
                        if (!nameInput.value.trim() && !qtyInput.value.trim()) {
                            ingsContainer.innerHTML = '';
                        }
                    }

                    for (let i = startIndex; i < json.length; i++) {
                        const row = json[i];
                        if (row && row.length > 0) {
                            const name = row[0] || '';
                            const qty = row[1] || '';
                            if (name) {
                                addIngredientRow(`${name} — ${qty}`);
                            }
                        }
                    }
                } catch (error) {
                    console.error("Lỗi đọc file Excel:", error);
                    alert("Có lỗi xảy ra khi đọc file Excel. Vui lòng đảm bảo file đúng định dạng.");
                }
                
                uploadExcelInput.value = ''; // Reset input file
            };
            reader.readAsArrayBuffer(file);
        });
    }

    function addIngredientRow(value) {
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.gap = '10px';
        
        const [name, qty] = value ? value.split(' — ') : ['', ''];
        
        row.innerHTML = `
            <input type="text" class="form-input ing-name" placeholder="Tên nguyên liệu..." style="flex: 2" value="${name || ''}">
            <input type="text" class="form-input ing-qty" placeholder="Số lượng..." style="flex: 1" value="${qty || ''}">
            <button type="button" class="btn-icon delete" onclick="this.parentElement.remove()"><i class="fa-solid fa-trash"></i></button>
        `;
        ingsContainer.appendChild(row);
    }

    if (foodForm) {
        foodForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errDiv = document.getElementById('fa-error');
            errDiv.classList.add('hidden');

            const id = document.getElementById('fa-id').value;
            
            const ings = [];
            ingsContainer.querySelectorAll('div').forEach(row => {
                const n = row.querySelector('.ing-name').value.trim();
                const q = row.querySelector('.ing-qty').value.trim();
                if(n) ings.push({ TenNguyenLieu: n, SoLuong: q });
            });

            const data = {
                TenMonAn: document.getElementById('fa-name').value,
                PhanLoai: document.getElementById('fa-cate').value,
                MoTa: document.getElementById('fa-desc').value,
                IsDeleted: document.getElementById('fa-deleted').value,
                DinhDuong: {
                    Calo: document.getElementById('fa-cal').value || 0,
                    Protein: document.getElementById('fa-pro').value || 0,
                    ChatBeo: document.getElementById('fa-fat').value || 0,
                    Carbohydrate: document.getElementById('fa-car').value || 0,
                    Vitamin: ''
                },
                CongThuc: {
                    HuongDan: document.getElementById('fa-instruct').value,
                    ThoiGianNau: 30, // Default estimate
                    KhauPhan: 1,
                    NguyenLieu: ings
                }
            };

            try {
                const url = id ? `/api/admin/foods/${id}` : '/api/admin/foods';
                const method = id ? 'PUT' : 'POST';
                
                const res = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const responseData = await res.json();
                if(responseData.success) {
                    adminModalOverlay.classList.add('hidden');
                    fetchAdminFoods();
                } else {
                    errDiv.textContent = responseData.message || 'Lỗi lưu dữ liệu';
                    errDiv.classList.remove('hidden', 'success');
                }
            } catch(error) {
                errDiv.textContent = 'Lỗi kết nối máy chủ';
                errDiv.classList.remove('hidden', 'success');
            }
        });
    }

    // Global Edit/Delete Handlers
    window.editAdminFood = async (id) => {
        try {
            const res = await fetch(`/api/admin/foods/${id}`);
            const responseData = await res.json();
            if(responseData.success) {
                const f = responseData.food;
                
                // Support both uppercase (backend format) and lowercase (PostgreSQL format)
                document.getElementById('fa-id').value = f.MaMonAn || f.mamonan || id;
                document.getElementById('fa-name').value = f.TenMonAn || f.tenmonan || '';
                document.getElementById('fa-cate').value = f.PhanLoai || f.phanloai || '';
                document.getElementById('fa-desc').value = f.MoTa || f.mota || '';
                document.getElementById('fa-deleted').value = (f.IsDeleted !== undefined ? f.IsDeleted : (f.isdeleted !== undefined ? f.isdeleted : 0));
                
                const nutrition = f.DinhDuong || f.dinhduong || {};
                document.getElementById('fa-cal').value = nutrition.Calo || nutrition.calo || '';
                document.getElementById('fa-pro').value = nutrition.Protein || nutrition.protein || '';
                document.getElementById('fa-fat').value = nutrition.ChatBeo || nutrition.chatbeo || '';
                document.getElementById('fa-car').value = nutrition.Carbohydrate || nutrition.carbohydrate || '';
                
                const recipe = f.CongThuc || f.congthuc || {};
                document.getElementById('fa-instruct').value = recipe.HuongDan || recipe.huongdan || '';
                
                ingsContainer.innerHTML = '';
                const ingredients = recipe.NguyenLieu || recipe.nguyenlieu || [];
                if(ingredients && ingredients.length > 0) {
                    ingredients.forEach(nl => {
                        const name = nl.TenNguyenLieu || nl.tennguyenlieu || '';
                        const amount = nl.SoLuong || nl.soluong || '';
                        addIngredientRow(`${name} — ${amount}`);
                    });
                } else {
                    addIngredientRow('');
                }

                document.getElementById('food-modal-title').textContent = 'Sửa Món Ăn (ID: ' + id + ')';
                adminModalOverlay.classList.remove('hidden');
            } else {
                alert("Không tải được chi tiết món ăn!");
            }
        } catch(e) { 
            console.error('Edit food error:', e); 
            alert("Lỗi kết nối máy chủ: " + e.message); 
        }
    };

    window.deleteAdminFood = async (id) => {
        if(!confirm('Bạn có chắc chắn muốn CHUYỂN VÀO THÙNG RÁC món ăn này? (Sẽ không còn hiện trên web cho User)')) return;
        try {
            const res = await fetch(`/api/admin/foods/${id}`, { method: 'DELETE' });
            const r = await res.json();
            if(r.success) fetchAdminFoods();
            else alert(r.message);
        } catch(e) { console.error(e); }
    };

    window.restoreAdminFood = async (id) => {
        if(!confirm('Bạn muốn HOÀN TÁC (khôi phục) món ăn này để hiển thị lại trên web?')) return;
        try {
            const res = await fetch(`/api/admin/foods/${id}/restore`, { method: 'PUT' });
            const r = await res.json();
            if(r.success) fetchAdminFoods();
            else alert(r.message);
        } catch(e) { console.error(e); }
    };

    window.hardDeleteAdminFood = async (id) => {
        if(!confirm('⚠️ BẠN CÓ CHẮC MUỐN XÓA VĨNH VIỄN MÓN ĂN NÀY?\n\nHành động này KHÔNG THỂ HOÀN TÁC!\nTất cả dữ liệu dinh dưỡng, công thức, nguyên liệu liên quan sẽ bị xóa hoàn toàn.')) return;
        if(!confirm('Xác nhận lần cuối: XÓA VĨNH VIỄN món ăn ID #' + id + '?')) return;
        try {
            const res = await fetch(`/api/admin/foods/${id}/hard-delete`, { method: 'DELETE' });
            const r = await res.json();
            if(r.success) {
                alert('✅ ' + r.message);
                fetchAdminFoods();
            }
            else alert(r.message);
        } catch(e) { console.error(e); }
    };

    window.deleteAdminUser = async (id) => {
        if(!confirm('Bạn có chắc chắn muốn XÓA VĨNH VIỄN người dùng này?')) return;
        try {
            const res = await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
            const r = await res.json();
            if(r.success) fetchAdminUsers();
            else alert(r.message);
        } catch(e) { console.error(e); }
    };

    // Default fetch on load
    fetchAdminStats();

    // Fetch Functions
    async function fetchAdminStats() {
        try {
            const res = await fetch('/api/admin/stats');
            const data = await res.json();
            if(data.success) {
                document.getElementById('st-users').textContent = data.stats.total_users;
                document.getElementById('st-foods').textContent = data.stats.total_foods;
                document.getElementById('st-recs').textContent = data.stats.total_recognitions;
            }
        } catch(e) { console.error(e); }
    }

    async function fetchAdminFoods() {
        const tb = document.getElementById('tb-foods');
        tb.innerHTML = '<tr><td colspan="5" style="text-align:center"><i class="fa-solid fa-spinner fa-spin"></i></td></tr>';
        selectedFoodIds.clear();
        updateBulkUI();
        try {
            const res = await fetch('/api/admin/foods');
            const data = await res.json();
            if(data.success) {
                tb.innerHTML = '';
                data.foods.forEach(f => {
                    const status = f.is_deleted ? '<span class="badge badge-danger">Đã khóa</span>' : '<span class="badge badge-success">Hiển thị</span>';
                    const tr = document.createElement('tr');
                    tr.dataset.foodId = f.id;
                    tr.innerHTML = `
                            <td>#${f.id}</td>
                            <td>${f.name}</td>
                            <td>${f.category}</td>
                            <td>${status}</td>
                            <td>
                                <div class="action-btns">
                                    <button class="btn-icon" title="Sửa" onclick="editAdminFood(${f.id})"><i class="fa-solid fa-pen"></i></button>
                                    ${!f.is_deleted ? `<button class="btn-icon delete" title="Khóa (Soft Delete)" onclick="deleteAdminFood(${f.id})"><i class="fa-solid fa-ban"></i></button>` : `<button class="btn-icon" title="Hoàn tác" style="color: var(--c-carb);" onclick="restoreAdminFood(${f.id})"><i class="fa-solid fa-rotate-left"></i></button>`}
                                    <button class="btn-icon delete" title="Xóa vĩnh viễn" onclick="hardDeleteAdminFood(${f.id})" style="color: #ef4444;"><i class="fa-solid fa-trash"></i></button>
                                    <label class="bulk-select-label" title="Chọn để xóa nhiều">
                                        <input type="checkbox" class="food-row-checkbox" data-food-id="${f.id}">
                                        <span class="bulk-select-box"><i class="fa-solid fa-check"></i></span>
                                    </label>
                                </div>
                            </td>
                    `;
                    tb.appendChild(tr);
                });
                // Attach checkbox listeners
                document.querySelectorAll('.food-row-checkbox').forEach(cb => {
                    cb.addEventListener('change', (e) => {
                        toggleFoodSelect(parseInt(e.target.dataset.foodId), e.target.checked);
                    });
                });
            }
        } catch(e) { console.error(e); tb.innerHTML = '<tr><td colspan="5" style="text-align:center; color:red;">Lỗi tải dữ liệu</td></tr>'; }
    }

    async function fetchAdminUsers() {
        const tb = document.getElementById('tb-users');
        tb.innerHTML = '<tr><td colspan="6" style="text-align:center"><i class="fa-solid fa-spinner fa-spin"></i></td></tr>';
        try {
            const res = await fetch('/api/admin/users');
            const data = await res.json();
            if(data.success) {
                tb.innerHTML = '';
                data.users.forEach(u => {
                    const status = u.role === 'admin' ? '<span class="badge badge-warning"><i class="fa-solid fa-star"></i> Admin</span>' : '<span class="badge badge-info">User</span>';
                    tb.innerHTML += `
                        <tr>
                            <td>#${u.id}</td>
                            <td style="font-weight: 500">${u.name}</td>
                            <td>${u.email}</td>
                            <td>${status}</td>
                            <td>${u.created_at}</td>
                            <td>
                                <div class="action-btns">
                                    <button class="btn-icon delete" title="Xóa" onclick="deleteAdminUser(${u.id})"><i class="fa-solid fa-trash"></i></button>
                                </div>
                            </td>
                        </tr>
                    `;
                });
            }
        } catch(e) { console.error(e); }
    }

    // ============================================
    // HISTORY: GRID + TABLE + DETAIL MODAL
    // ============================================
    let allHistoryData = [];
    let historyView = 'grid'; // 'grid' or 'table'

    // View toggle
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            historyView = btn.dataset.view;
            const gridEl = document.getElementById('history-grid-view');
            const tableEl = document.getElementById('history-table-view');
            if (historyView === 'grid') {
                gridEl.style.display = '';
                tableEl.style.display = 'none';
            } else {
                gridEl.style.display = 'none';
                tableEl.style.display = '';
            }
        });
    });

    // Search filter
    const historySearchInput = document.getElementById('history-search-input');
    if (historySearchInput) {
        let searchTimeout;
        historySearchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                renderHistoryViews(allHistoryData, historySearchInput.value.trim().toLowerCase());
            }, 300);
        });
    }

    function renderHistoryViews(data, filter = '') {
        let filtered = data;
        if (filter) {
            filtered = data.filter(h =>
                (h.food_name || '').toLowerCase().includes(filter) ||
                (h.user_name || '').toLowerCase().includes(filter) ||
                (h.user_email || '').toLowerCase().includes(filter)
            );
        }
        renderHistoryGrid(filtered);
        renderHistoryTable(filtered);
    }

    function getImageSrc(imageData) {
        if (!imageData) return '';
        if (imageData.startsWith('data:')) return imageData;
        if (imageData.startsWith('/9j/') || imageData.startsWith('iVBOR')) {
            return 'data:image/jpeg;base64,' + imageData;
        }
        return imageData;
    }

    function getRatingBadge(rating) {
        if (!rating) return '<span class="rating-badge rating-none"><i class="fa-solid fa-minus"></i> Chưa đánh giá</span>';
        const map = {
            'chinh_xac': { cls: 'rating-green', icon: 'fa-circle-check', text: 'Chính xác' },
            'trung_binh': { cls: 'rating-yellow', icon: 'fa-minus-circle', text: 'Trung bình' },
            'sai': { cls: 'rating-red', icon: 'fa-circle-xmark', text: 'Sai kết quả' }
        };
        const r = map[rating] || map['chinh_xac'];
        return `<span class="rating-badge ${r.cls}"><i class="fa-solid ${r.icon}"></i> ${r.text}</span>`;
    }

    function renderHistoryGrid(data) {
        const grid = document.getElementById('history-grid-view');
        if (data.length === 0) {
            grid.innerHTML = `
                <div class="history-empty">
                    <i class="fa-solid fa-clock-rotate-left"></i>
                    <p>Chưa có lịch sử nhận diện nào</p>
                </div>`;
            return;
        }

        grid.innerHTML = data.map(h => {
            const imgSrc = getImageSrc(h.image);
            const hasImage = !!imgSrc;
            const dateObj = h.time ? new Date(h.time) : null;
            const dateStr = dateObj ? dateObj.toLocaleDateString('vi-VN') : '';
            const timeStr = dateObj ? dateObj.toLocaleTimeString('vi-VN', {hour: '2-digit', minute: '2-digit'}) : '';
            
            return `
            <div class="history-card" onclick="viewHistoryDetail(${h.id})">
                <input type="checkbox" class="history-check" data-id="${h.id}" onclick="event.stopPropagation(); updateBulkSelection()">
                <div class="history-card-img">
                    ${hasImage 
                        ? `<img src="${imgSrc}" alt="${h.food_name}" loading="lazy">` 
                        : `<div class="history-card-no-img"><i class="fa-solid fa-image"></i></div>`
                    }
                </div>
                <div class="history-card-body">
                    <h4 class="history-card-food">${h.food_name || 'Không xác định'}</h4>
                    <div class="history-card-meta">
                        <span class="history-card-user">
                            <i class="fa-solid fa-user"></i> ${h.user_name}
                        </span>
                        ${h.calories ? `<span class="history-card-cal"><i class="fa-solid fa-fire-flame-curved"></i> ${Math.round(h.calories)} kcal</span>` : ''}
                    </div>
                    <div class="history-card-rating">${getRatingBadge(h.user_rating)}</div>
                    <div class="history-card-time">
                        <i class="fa-regular fa-clock"></i> ${dateStr} ${timeStr}
                    </div>
                </div>
                <div class="history-card-hover-hint">
                    <i class="fa-solid fa-eye"></i> Xem chi tiết
                </div>
                <button class="history-card-delete" title="Xóa" onclick="event.stopPropagation(); deleteHistoryRecord(${h.id})">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>`;
        }).join('');
    }

    function renderHistoryTable(data) {
        const tb = document.getElementById('tb-history');
        if (data.length === 0) {
            tb.innerHTML = '<tr><td colspan="9" style="text-align:center; padding: 40px; color: var(--text-muted);">Không có dữ liệu</td></tr>';
            return;
        }
        tb.innerHTML = data.map(h => {
            const imgSrc = getImageSrc(h.image);
            const dateObj = h.time ? new Date(h.time) : null;
            const dateStr = dateObj ? dateObj.toLocaleString('vi-VN') : '';
            return `
            <tr>
                <td><input type="checkbox" class="history-check" data-id="${h.id}" onclick="updateBulkSelection()"></td>
                <td>#${h.id}</td>
                <td>
                    ${imgSrc 
                        ? `<img src="${imgSrc}" alt="" class="history-table-thumb" onclick="event.stopPropagation(); viewHistoryDetail(${h.id})">` 
                        : `<span class="history-table-no-img"><i class="fa-solid fa-image-slash"></i></span>`
                    }
                </td>
                <td>${h.user_name}</td>
                <td style="font-weight:500; color:var(--primary-light)">${h.food_name}</td>
                <td>${h.calories ? Math.round(h.calories) + ' kcal' : '--'}</td>
                <td>${getRatingBadge(h.user_rating)}</td>
                <td><span style="font-size: 13px; color: var(--text-muted);">${dateStr}</span></td>
                <td>
                    <button class="btn-icon" title="Xem chi tiết" onclick="viewHistoryDetail(${h.id})">
                        <i class="fa-solid fa-eye"></i>
                    </button>
                    <button class="btn-icon btn-icon-danger" title="Xóa" onclick="deleteHistoryRecord(${h.id})">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </td>
            </tr>`;
        }).join('');
    }

    async function fetchAdminHistory() {
        const grid = document.getElementById('history-grid-view');
        const tb = document.getElementById('tb-history');
        grid.innerHTML = '<div class="history-loading"><i class="fa-solid fa-spinner fa-spin"></i><span>Đang tải dữ liệu...</span></div>';
        tb.innerHTML = '<tr><td colspan="9" style="text-align:center"><i class="fa-solid fa-spinner fa-spin"></i></td></tr>';
        try {
            const res = await fetch('/api/admin/history');
            const data = await res.json();
            if(data.success) {
                allHistoryData = data.history;
                const filter = (historySearchInput && historySearchInput.value.trim().toLowerCase()) || '';
                renderHistoryViews(allHistoryData, filter);
            }
        } catch(e) { 
            console.error(e); 
            grid.innerHTML = '<div class="history-empty"><i class="fa-solid fa-triangle-exclamation"></i><p>Lỗi tải dữ liệu</p></div>';
        }
    }

    // Listen for refresh event (from global deleteHistoryRecord)
    document.addEventListener('refreshHistory', () => fetchAdminHistory());

    // Detail modal
    window.viewHistoryDetail = async (historyId) => {
        const overlay = document.getElementById('history-detail-overlay');
        const content = document.getElementById('history-detail-content');
        overlay.classList.remove('hidden');
        content.innerHTML = '<div class="history-loading"><i class="fa-solid fa-spinner fa-spin"></i><span>Đang tải chi tiết...</span></div>';

        try {
            const res = await fetch(`/api/admin/history/${historyId}`);
            const data = await res.json();
            if (!data.success) {
                content.innerHTML = '<div class="history-empty"><i class="fa-solid fa-circle-exclamation"></i><p>Không tìm thấy bản ghi</p></div>';
                return;
            }

            const d = data.detail;
            const imgSrc = getImageSrc(d.image);
            const dateObj = d.time ? new Date(d.time) : null;
            const dateStr = dateObj ? dateObj.toLocaleString('vi-VN') : 'N/A';
            const fi = d.food_info; // may be null

            content.innerHTML = `
                <div class="hd-header">
                    <div class="hd-badge"><i class="fa-solid fa-receipt"></i> Chi Tiết Nhận Diện #${d.id}</div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span class="hd-time"><i class="fa-regular fa-clock"></i> ${dateStr}</span>
                        <button class="btn-admin-delete" onclick="deleteHistoryRecord(${d.id})" title="Xóa bản ghi">
                            <i class="fa-solid fa-trash-can"></i> Xóa
                        </button>
                    </div>
                </div>

                <div class="hd-layout">
                    <!-- Image Section -->
                    <div class="hd-image-section">
                        ${imgSrc 
                            ? `<div class="hd-image-wrap"><img src="${imgSrc}" alt="${d.food_name}" class="hd-image"></div>`
                            : `<div class="hd-image-placeholder"><i class="fa-solid fa-camera"></i><span>Không có hình ảnh</span></div>`
                        }
                    </div>

                    <!-- Info Section -->
                    <div class="hd-info-section">
                        <!-- Food Name -->
                        <h2 class="hd-food-name">
                            <i class="fa-solid fa-utensils"></i>
                            ${d.food_name || 'Không xác định'}
                        </h2>

                        <!-- User Rating Badge -->
                        <div class="hd-user-rating">
                            <span class="hd-info-label">Đánh giá người dùng:</span>
                            ${getRatingBadge(d.user_rating)}
                        </div>

                        <!-- User Info -->
                        <div class="hd-info-card">
                            <div class="hd-info-card-title"><i class="fa-solid fa-user-circle"></i> Người dùng</div>
                            <div class="hd-info-row">
                                <span class="hd-info-label">Tên:</span>
                                <span class="hd-info-value">${d.user_name}</span>
                            </div>
                            ${d.user_email ? `
                            <div class="hd-info-row">
                                <span class="hd-info-label">Email:</span>
                                <span class="hd-info-value">${d.user_email}</span>
                            </div>` : ''}
                            ${d.user_id ? `
                            <div class="hd-info-row">
                                <span class="hd-info-label">User ID:</span>
                                <span class="hd-info-value">#${d.user_id}</span>
                            </div>` : ''}
                        </div>

                        <!-- Admin Edit Form -->
                        <div class="hd-info-card hd-edit-card">
                            <div class="hd-info-card-title"><i class="fa-solid fa-pen-to-square"></i> Chỉnh sửa thông tin</div>
                            <div class="hd-edit-form">
                                <div class="hd-edit-group">
                                    <label>Tên món ăn</label>
                                    <input type="text" id="hd-edit-name" class="hd-edit-input" value="${(d.food_name || '').replace(/"/g, '&quot;')}">
                                </div>
                                <div class="hd-edit-group">
                                    <label>Calo (kcal)</label>
                                    <input type="number" id="hd-edit-cal" class="hd-edit-input" value="${d.calories ? Math.round(d.calories) : ''}" placeholder="VD: 350">
                                </div>
                                <button class="btn-admin-save" id="hd-edit-save" data-id="${d.id}">
                                    <i class="fa-solid fa-floppy-disk"></i> Lưu & Thông báo
                                </button>
                                <div class="hd-edit-msg hidden" id="hd-edit-msg"></div>
                            </div>
                        </div>

                        <!-- Detailed Nutrition from DB -->
                        ${fi ? `
                        <div class="hd-info-card hd-nutrition-card">
                            <div class="hd-info-card-title"><i class="fa-solid fa-chart-pie"></i> Thông tin dinh dưỡng (CSDL)</div>
                            ${fi.category ? `<div class="hd-info-row"><span class="hd-info-label">Phân loại:</span><span class="hd-info-value">${fi.category}</span></div>` : ''}
                            ${fi.description ? `<div class="hd-info-row"><span class="hd-info-label">Mô tả:</span><span class="hd-info-value hd-desc">${fi.description}</span></div>` : ''}
                            <div class="hd-nutrition-grid">
                                <div class="hd-nutr-item hd-nutr-cal">
                                    <i class="fa-solid fa-fire"></i>
                                    <span class="hd-nutr-val">${fi.calories || 0}</span>
                                    <span class="hd-nutr-label">Calo</span>
                                </div>
                                <div class="hd-nutr-item hd-nutr-pro">
                                    <i class="fa-solid fa-dumbbell"></i>
                                    <span class="hd-nutr-val">${fi.protein || 0}g</span>
                                    <span class="hd-nutr-label">Protein</span>
                                </div>
                                <div class="hd-nutr-item hd-nutr-fat">
                                    <i class="fa-solid fa-droplet"></i>
                                    <span class="hd-nutr-val">${fi.fat || 0}g</span>
                                    <span class="hd-nutr-label">Chất béo</span>
                                </div>
                                <div class="hd-nutr-item hd-nutr-carb">
                                    <i class="fa-solid fa-wheat-awn"></i>
                                    <span class="hd-nutr-val">${fi.carbs || 0}g</span>
                                    <span class="hd-nutr-label">Carbs</span>
                                </div>
                            </div>
                        </div>` : `
                        <div class="hd-info-card">
                            <div class="hd-info-card-title"><i class="fa-solid fa-circle-info"></i> Thông tin CSDL</div>
                            <p style="color: var(--text-muted); font-size: 14px;">Món ăn này chưa có trong cơ sở dữ liệu hệ thống.</p>
                        </div>`}
                    </div>
                </div>
            `;

            // Attach save handler
            const saveBtn = document.getElementById('hd-edit-save');
            saveBtn?.addEventListener('click', async () => {
                const hId = saveBtn.dataset.id;
                const newName = document.getElementById('hd-edit-name').value.trim();
                const newCal = document.getElementById('hd-edit-cal').value;
                const msgDiv = document.getElementById('hd-edit-msg');
                
                if (!newName) {
                    msgDiv.textContent = 'Tên món ăn không được trống';
                    msgDiv.className = 'hd-edit-msg hd-edit-error';
                    return;
                }

                saveBtn.disabled = true;
                saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...';

                try {
                    const res = await fetch(`/api/admin/history/${hId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ food_name: newName, calories: newCal || null })
                    });
                    const result = await res.json();
                    
                    if (result.success) {
                        msgDiv.textContent = '✅ ' + result.message;
                        msgDiv.className = 'hd-edit-msg hd-edit-success';
                        // Refresh history list
                        fetchAdminHistory();
                    } else {
                        msgDiv.textContent = '❌ ' + result.message;
                        msgDiv.className = 'hd-edit-msg hd-edit-error';
                    }
                } catch(err) {
                    msgDiv.textContent = '❌ Lỗi kết nối server';
                    msgDiv.className = 'hd-edit-msg hd-edit-error';
                }

                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Lưu & Thông báo';
            });
        } catch(e) {
            console.error('History detail error:', e);
            content.innerHTML = '<div class="history-empty"><i class="fa-solid fa-triangle-exclamation"></i><p>Lỗi khi tải chi tiết</p></div>';
        }
    };
});

// Global: Xóa bản ghi lịch sử
async function deleteHistoryRecord(historyId) {
    if (!confirm('Bạn có chắc muốn xóa bản ghi lịch sử này?')) return;
    
    try {
        const res = await fetch(`/api/admin/history/${historyId}`, { method: 'DELETE' });
        const data = await res.json();
        
        if (data.success) {
            // Close detail modal if open
            const overlay = document.getElementById('history-detail-overlay');
            if (overlay) overlay.classList.add('hidden');
            
            // Trigger re-fetch
            document.dispatchEvent(new Event('refreshHistory'));
            alert('✅ ' + data.message);
        } else {
            alert('❌ ' + data.message);
        }
    } catch(e) {
        console.error('Delete error:', e);
        alert('❌ Lỗi kết nối server');
    }
}

// Global: Cập nhật nút xóa hàng loạt
function updateBulkSelection() {
    const checks = document.querySelectorAll('.history-check:checked');
    const btn = document.getElementById('bulk-delete-btn');
    const allChecks = document.querySelectorAll('.history-check');
    const tableSelectAll = document.getElementById('table-select-all');
    
    const count = checks.length;
    
    if (btn) {
        btn.innerHTML = `<i class="fa-solid fa-trash-can"></i> Xóa (${count})`;
        if (count > 0) {
            btn.disabled = false;
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        } else {
            btn.disabled = true;
            btn.style.opacity = '0.4';
            btn.style.pointerEvents = 'none';
        }
    }
    
    // Sync select-all checkbox
    const allChecked = allChecks.length > 0 && count === allChecks.length;
    if (tableSelectAll) tableSelectAll.checked = allChecked;
}

// Select all handler (table header checkbox)
document.addEventListener('change', (e) => {
    if (e.target.id === 'table-select-all') {
        const checked = e.target.checked;
        document.querySelectorAll('.history-check').forEach(cb => { cb.checked = checked; });
        updateBulkSelection();
    }
});

// Bulk delete button
document.addEventListener('click', async (e) => {
    const btn = e.target.closest('#bulk-delete-btn');
    if (!btn) return;
    
    const checks = document.querySelectorAll('.history-check:checked');
    const ids = Array.from(checks).map(cb => parseInt(cb.dataset.id));
    
    if (ids.length === 0) return;
    if (!confirm(`Bạn có chắc muốn xóa ${ids.length} bản ghi lịch sử?`)) return;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang xóa...';
    
    try {
        const res = await fetch('/api/admin/history/bulk-delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids })
        });
        const data = await res.json();
        
        if (data.success) {
            document.dispatchEvent(new Event('refreshHistory'));
            updateBulkSelection();
            alert('✅ ' + data.message);
        } else {
            alert('❌ ' + data.message);
        }
    } catch(e) {
        console.error('Bulk delete error:', e);
        alert('❌ Lỗi kết nối server');
    }
    
    btn.disabled = false;
    updateBulkSelection();
});
