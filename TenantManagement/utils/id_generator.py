def generate_tenant_id(existing_tenants):
    if not existing_tenants:
        return "T-001"

    max_num = 0
    for tenant in existing_tenants:
        try:
            if tenant.tenant_id.startswith("T-"):
                num_part = int(tenant.tenant_id.split("-")[1])
                if num_part > max_num:
                    max_num = num_part
        except (ValueError, IndexError):
            continue
    next_id = f"T-{str(max_num + 1).zfill(3)}"
    return next_id
