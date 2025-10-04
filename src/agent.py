import re

def decompose_query(query):
    query = query.strip().lower()
    sub_queries = []
    
    if any(word in query for word in ["which company", "highest", "lowest", "compare"]):
        companies = ["microsoft", "google", "nvidia"]
        metric_patterns = [
            "operating margin", "revenue", "gross margin", "r&d spending", 
            "cloud revenue", "data center revenue", "ai investment"
        ]
        
        for metric in metric_patterns:
            if metric in query:
                for company in companies:
                    sub_queries.append(f"{company} {metric}")
                break
        
        if not sub_queries:
            for company in companies:
                sub_queries.append(f"{company} " + query.replace("which company", "").replace("compare", ""))
    
    elif any(word in query for word in ["grow", "growth", "change", "from", "to"]):
        years = re.findall(r'20\d{2}', query)
        if len(years) >= 2:
            metric = query
            for year in years:
                metric = metric.replace(year, "").strip()
            
            for year in years:
                sub_queries.append(f"{metric} {year}")
        else:
            sub_queries = [query]
    
    elif "across all" in query or "all three companies" in query:
        companies = ["microsoft", "google", "nvidia"]
        base_query = query.replace("across all", "").replace("all three companies", "").strip()
        
        for company in companies:
            sub_queries.append(f"{company} {base_query}")
    
    elif "percentage" in query or "%" in query:
        sub_queries = [query]
    
    else:
        sub_queries = [query]
    
    sub_queries = [sq.strip() for sq in sub_queries if sq.strip()]
    
    if not sub_queries:
        sub_queries = [query]
    
    return sub_queries
