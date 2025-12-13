import requests
import os

def update_rules():
    # --- 配置区域 ---
    # 这里使用了你脚本1中完整的规则源列表
    URLS_TO_FETCH = [
        "https://raw.githubusercontent.com/sykin7/my-telegram-spam-rules/refs/heads/main/spam.txt",
        "https://raw.githubusercontent.com/spamkeywords/keywords/main/keywords.txt",
        "https://raw.githubusercontent.com/roumilb/spam_words_api_lists/main/spam_words_lists",
        "https://raw.githubusercontent.com/fwwdn/sensitive-stop-words/master/广告.txt",
        "https://raw.githubusercontent.com/iamlos/negative-email-keywords-masterlist/main/negative_keywords.txt",
        "https://raw.githubusercontent.com/matomo-org/referrer-spam-list/master/spammers.txt"
    ]
    
    FILE_PATH = "spam.txt"
    all_rules_set = set() # 使用集合自动去重
    
    print("--- 正在初始化规则库 ---")

    # 1. 读取本地现有的规则 (如果有)
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    # 清理逻辑：去空格，转小写
                    clean_line = line.strip().lower()
                    # 严谨逻辑：排除空行、排除注释(#)和(!)，防止把注释当成垃圾词
                    if clean_line and not clean_line.startswith('#') and not clean_line.startswith('!'):
                        all_rules_set.add(clean_line)
            print(f"✅ 已加载本地规则，当前共 {len(all_rules_set)} 条。")
        except Exception as e:
            print(f"⚠️ 读取本地文件出错: {e}")

    # 2. 从网络抓取新规则
    print(f"--- 开始从 {len(URLS_TO_FETCH)} 个源抓取更新 ---")
    
    for url in URLS_TO_FETCH:
        try:
            # 设置超时时间，防止卡死
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            
            added_count = 0
            for line in resp.text.splitlines():
                clean_line = line.strip().lower()
                # 同样的严谨过滤逻辑
                if clean_line and not clean_line.startswith('#') and not clean_line.startswith('!'):
                    if clean_line not in all_rules_set:
                        added_count += 1
                    all_rules_set.add(clean_line)
            
            print(f"  > 抓取成功 [{url.split('/')[-1]}]: 新增 {added_count} 条")
            
        except requests.exceptions.RequestException as e:
            print(f"  > ❌ 抓取失败，跳过: {url}")
            # 这里不打印详细错误堆栈，保持界面整洁，除非你需要调试

    # 3. 准备写入文件
    if not all_rules_set:
        print("⚠️ 没有收集到任何规则，跳过更新。")
        return

    # 排序：让文件看起来整洁有序
    sorted_rules = sorted(list(all_rules_set))
    new_content = "\n".join(sorted_rules)
    
    # 4. 智能对比：只有内容真的变了才写入，减少磁盘损耗
    old_content_clean = ""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            # 读取旧文件并用同样的逻辑处理，确保对比准确
            old_lines = [l.strip().lower() for l in f if l.strip() and not l.startswith('#') and not l.startswith('!')]
            old_content_clean = "\n".join(sorted(set(old_lines)))

    if new_content != old_content_clean:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"\n🎉 更新完成！文件 {FILE_PATH} 已更新。")
        print(f"📊 总规则数: {len(sorted_rules)}")
    else:
        print(f"\n⏸️ 规则没有变化，无需更新文件。当前总数: {len(sorted_rules)}")

if __name__ == "__main__":
    update_rules()
