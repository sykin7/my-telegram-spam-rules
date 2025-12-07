import requests
import os

def update_rules():
    # 高频更新的规则原始网址列表 (Raw URLs)
    URLS_TO_FETCH = [
        # 规则源 1: LDNOOBW 通用英文不良词汇 (更新频率极高，几乎每天都有贡献者)
        "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en",
        
        # 规则源 2: StopForumSpam 活跃垃圾邮件域名/IP 黑名单 (用于网络威胁，更新极快)
        "https://raw.githubusercontent.com/raghur/No-Track/master/host", 

        # 规则源 3: Bad-Words-List 通用词汇列表 (社区维护稳定，定期更新)
        "https://raw.githubusercontent.com/Syed-Muhammad-Saad/Bad-Words-List/main/bad_words.txt"
    ]
    
    FILE_PATH = "spam.txt"
    all_rules_set = set() # 规则集合：用于自动去重
    fetch_success_count = 0

    # -----------------------------------------------------------
    # 关键修改：步骤 1. 首先加载并保留现有规则
    # -----------------------------------------------------------
    existing_rules_count = 0
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                existing_content = f.read()
                
            for rule in existing_content.splitlines():
                # 清理并添加到集合中：保留了现有规则，并进行了去重和规范化
                cleaned_rule = rule.strip().lower()
                # 排除空行、以 # 和 ! 开头的注释行
                if cleaned_rule and not cleaned_rule.startswith('#') and not cleaned_rule.startswith('!'):
                    all_rules_set.add(cleaned_rule)
                    existing_rules_count += 1
            print(f"已加载 {existing_rules_count} 条现有规则到总集合中。")
        except Exception as e:
            print(f"警告: 读取现有文件 {FILE_PATH} 失败。错误: {e}")

    print("--- 开始多源规则抓取 ---")

    # -----------------------------------------------------------
    # 步骤 2. 抓取新规则并添加到同一集合中
    # -----------------------------------------------------------
    for url in URLS_TO_FETCH:
        try:
            print(f"正在抓取: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            rules_from_source = response.text.splitlines()
            new_rules_added = 0
            
            for rule in rules_from_source:
                # 规则清理：去除首尾空白，转换为小写
                cleaned_rule = rule.strip().lower()
                if cleaned_rule and not cleaned_rule.startswith('#') and not cleaned_rule.startswith('!'):
                    # 检查规则是否为新加入的
                    if cleaned_rule not in all_rules_set:
                        new_rules_added += 1
                    all_rules_set.add(cleaned_rule)
            
            fetch_success_count += 1
            print(f"  > 抓取成功，新增 {new_rules_added} 条规则到总集合。")

        except requests.exceptions.RequestException as e:
            print(f"  > 抓取失败，跳过此网址: {url}。错误: {e}")

    # -----------------------------------------------------------
    # 步骤 3. 比较、排序和写入最终内容
    # -----------------------------------------------------------
    if not all_rules_set:
        print("警告: 最终规则集合为空，跳过文件更新。")
        return

    # 将集合转换成列表，按字母排序，然后用换行符连接
    sorted_unique_rules = sorted(list(all_rules_set))
    new_rules_content = "\n".join(sorted_unique_rules)
    total_final_count = len(sorted_unique_rules)
    print(f"--- 抓取完成。总共合并了 {total_final_count} 条唯一的现有及新规则。---")
    
    # 重新读取旧文件进行对比，确保对比的是当前已存在的文件内容
    old_rules_content_cleaned = ""
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                old_rules_raw = f.read()
            # 同样对旧文件的内容进行清理和排序，以实现准确的对比
            old_rules_list_for_comparison = sorted([r.strip().lower() for r in old_rules_raw.splitlines() if r.strip() and not r.strip().startswith('#') and not r.strip().startswith('!')])
            old_rules_content_cleaned = "\n".join(old_rules_list_for_comparison)
        except Exception:
            # 如果读取失败，强制写入以确保数据不丢失
            old_rules_content_cleaned = "ERROR_READING_OLD_FILE" 

    # 对比新旧内容，只有不同时才写入
    if new_rules_content != old_rules_content_cleaned:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            f.write(new_rules_content)
        
        print(f"✅ 成功更新 {FILE_PATH}。新规则总数：{total_final_count}")
    else:
        print(f"⏸️ {FILE_PATH} 内容与新合并后的规则相同，无需更新。")

if __name__ == "__main__":
    update_rules()
