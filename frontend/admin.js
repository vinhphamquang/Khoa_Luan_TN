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

    async function fetchAdminHistory() {
        const tb = document.getElementById('tb-history');
        tb.innerHTML = '<tr><td colspan="5" style="text-align:center"><i class="fa-solid fa-spinner fa-spin"></i></td></tr>';
        try {
            const res = await fetch('/api/admin/history');
            const data = await res.json();
            if(data.success) {
                tb.innerHTML = '';
                data.history.forEach(h => {
                    tb.innerHTML += `
                        <tr>
                            <td>#${h.id}</td>
                            <td>${h.user_name || 'Khách'}</td>
                            <td style="font-weight:500; color:var(--primary-light)">${h.food_name}</td>
                            <td><span class="badge badge-success">${h.accuracy}%</span></td>
                            <td><span style="font-size: 13px; color: var(--text-muted);">${new Date(h.time).toLocaleString()}</span></td>
                        </tr>
                    `;
                });
            }
        } catch(e) { console.error(e); }
    }
});
