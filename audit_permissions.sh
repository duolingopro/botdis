#!/usr/bin/env bash
#
# audit_permissions.sh - Quét các thư mục chỉ định, phát hiện file/thư mục
# có quyền quá mở (world-writable, 777, setuid/setgid...) và xuất báo cáo.
#
# Dùng:
#   ./audit_permissions.sh [thư_mục...]        # quét các thư mục đưa vào
#   ./audit_permissions.sh                     # không có tham số -> quét thư mục hiện tại
#
# Tùy chọn (biến môi trường):
#   REPORT_DIR=đường_dẫn   Thư mục xuất báo cáo (mặc định: ./reports)
#   INCLUDE_OCTAL=777,776  Danh sách quyền bát phân bị coi là "quá mở"
#   FOLLOW_SYMLINKS=1      Đi theo symlink (mặc định: 0, không đi theo)
#
set -euo pipefail

# ---------- Cấu hình ----------
REPORT_DIR="${REPORT_DIR:-./reports}"
FOLLOW_SYMLINKS="${FOLLOW_SYMLINKS:-0}"
# Các mode bát phân được coi là cấu hình sai (world-writable / quá mở)
IFS=',' read -r -a BAD_MODES <<< "${INCLUDE_OCTAL:-777,776,766,767,775}"

FIND_FOLLOW=()
[[ "$FOLLOW_SYMLINKS" == "1" ]] && FIND_FOLLOW=(-L)

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_FILE="${REPORT_DIR}/permission_audit_${TIMESTAMP}.txt"
CSV_FILE="${REPORT_DIR}/permission_audit_${TIMESTAMP}.csv"

mkdir -p "$REPORT_DIR"

# Các thư mục cần quét; mặc định là thư mục hiện tại
TARGETS=("$@")
[[ ${#TARGETS[@]} -eq 0 ]] && TARGETS=("$PWD")

# ---------- Helpers ----------
log() { printf '%s\n' "$*" | tee -a "$REPORT_FILE"; }

# Kiểm tra mode bát phân có nằm trong danh sách BAD_MODES không
is_bad_mode() {
    local mode="$1" bad
    for bad in "${BAD_MODES[@]}"; do
        [[ "$mode" == "$bad" ]] && return 0
    done
    return 1
}

# Fallback cho hệ thống không có GNU find -printf (macOS/BSD):
# dùng find + stat, in cùng định dạng: mode \t type \t owner \t group \t size \t path \0
stat_walk() {
    local root="$1" p mode ftype owner group size
    while IFS= read -r -d '' p; do
        # %Lp: quyền dạng ký tự, %LSp: quyền ký tự đầy đủ, %u/%g: owner/group, %z: size, %HT: loại
        if stat -f '%Lp%t%u%t%g%t%z%t%HT%t%N' -- "$p" >/dev/null 2>&1; then
            IFS=$'\t' read -r mode owner group size ftype p < <(stat -f '%Lp%t%u%t%g%t%z%t%HT%t%N' -- "$p")
        else
            # GNU stat
            IFS=$'\t' read -r mode owner group size ftype p < <(stat -c '%a%t%U%t%G%t%s%t%F%t%n' -- "$p")
        fi
        case "$ftype" in
            directory|dir) ftype="d" ;;
            *regular*|reg) ftype="f" ;;
            *link*)        ftype="l" ;;
            *)             ftype="o" ;;
        esac
        printf '%s\t%s\t%s\t%s\t%s\t%s\0' "$mode" "$ftype" "$owner" "$group" "$size" "$p"
    done < <(find "${FIND_FOLLOW[@]}" "$root" -print0 2>/dev/null)
}

# ---------- Header báo cáo ----------
: > "$REPORT_FILE"
log "=========================================================="
log " BÁO CÁO KIỂM TRA QUYỀN TẬP TIN (FILE PERMISSION AUDIT)"
log "=========================================================="
log "Thời gian     : $(date '+%Y-%m-%d %H:%M:%S')"
log "Người chạy    : $(id -un 2>/dev/null || echo 'n/a') (uid=$(id -u 2>/dev/null || echo '?'))"
log "Máy chủ       : $(hostname 2>/dev/null || echo 'n/a')"
log "Thư mục quét  : ${TARGETS[*]}"
log "Mode bị chặn  : ${BAD_MODES[*]}"
log "World-writable: cũng bị gắn cờ bất kể mode cụ thể"
log "Đi theo symlink: $FOLLOW_SYMLINKS"
log ""

printf 'path,mode,owner,group,type,size_bytes,reason\n' > "$CSV_FILE"

total_flagged=0
world_writable=0
setuid_count=0

# ---------- Quét ----------
for target in "${TARGETS[@]}"; do
    if [[ ! -e "$target" ]]; then
        log "[CẢNH BÁO] Bỏ qua đường dẫn không tồn tại: $target"
        continue
    fi

    log "----------------------------------------------------------"
    log "Đang quét: $target"
    log "----------------------------------------------------------"

    # Duyệt từng entry (in ra: mode bát phân \t loại \t owner \t group \t size \t path)
    # Dùng -print0 / read -d '' để an toàn với tên file có khoảng trắng/ký tự lạ.
    while IFS= read -r -d '' entry; do
        path="${entry##*$'\t'}"
        IFS=$'\t' read -r mode ftype owner group size _ <<< "$entry"

        reason=""

        # 1) Mode bát phân nằm trong danh sách quá mở
        if is_bad_mode "$mode"; then
            reason="mode quá mở ($mode)"
        fi

        # 2) World-writable (bit ghi của "other" = 2) bất kể mode cụ thể
        other_digit=$(( 8#${mode: -1} ))
        if (( other_digit & 2 )); then
            world_writable=$(( world_writable + 1 ))
            reason="${reason:+$reason; }world-writable"
        fi

        # 3) setuid / setgid trên file thực thi
        if [[ "$ftype" == "f" ]]; then
            # stat đã trả mode đầy đủ (gồm bit đặc biệt) nếu hệ thống hỗ trợ
            if [[ ${#mode} -ge 4 ]]; then
                special="${mode:0:1}"
                if [[ "$special" == "4" || "$special" == "5" || "$special" == "6" || "$special" == "7" ]]; then
                    setuid_count=$(( setuid_count + 1 ))
                    reason="${reason:+$reason; }setuid/setgid ($mode)"
                fi
            fi
        fi

        if [[ -n "$reason" ]]; then
            total_flagged=$(( total_flagged + 1 ))
            printf '%s\n' "  [$ftype] $path  mode=$mode owner=$owner group=$group size=$size -> $reason" | tee -a "$REPORT_FILE"
            # CSV: escape dấu phẩy trong path bằng cách bọc nháy
            safe_path="${path//\"/\"\"}"
            printf '"%s",%s,%s,%s,%s,%s,"%s"\n' \
                "$safe_path" "$mode" "$owner" "$group" "$ftype" "$size" "$reason" >> "$CSV_FILE"
        fi
    done < <(
        find "${FIND_FOLLOW[@]}" "$target" \
            -printf '%m\t%y\t%u\t%g\t%s\t%p\0' 2>/dev/null \
        || stat_walk "$target"
    )
    log ""
done

# ---------- Tổng kết ----------
log "=========================================================="
log " TỔNG KẾT"
log "=========================================================="
log "Tổng số entry bị gắn cờ : $total_flagged"
log "  - World-writable       : $world_writable"
log "  - Setuid/Setgid file   : $setuid_count"
log ""
log "Báo cáo đầy đủ : $REPORT_FILE"
log "Bản CSV        : $CSV_FILE"
log ""
if (( total_flagged > 0 )); then
    log "KHUYẾN NGHỊ:"
    log "  - File thường quá mở   -> chmod 644 (hoặc 640 nếu nhạy cảm)"
    log "  - Thư mục quá mở       -> chmod 755 (hoặc 750)"
    log "  - File chứa bí mật/.env-> chmod 600 và chown về user dịch vụ"
    log "  - setuid/setgid không cần thiết -> gỡ bằng chmod u-s,g-s"
    exit 1   # mã thoát khác 0 để pipeline/CI dễ phát hiện có lỗi
else
    log "Không phát hiện cấu hình quyền nguy hiểm. Trạng thái: SẠCH"
    exit 0
fi
