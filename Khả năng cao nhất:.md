Khả năng cao nhất:

❌ QFormer bottleneck (64 queries quá ít)

V-JEPA cho features phong phú → 64 queries không đủ compress
Fix: Tăng lên 128 queries


❌ Thiếu temporal encoding

V-JEPA features có temporal info → QFormer không biết order
Fix: Thêm learnable temporal embeddings


❌ Mismatch dimensions

V-JEPA output (1024?) → QFormer (768) → information loss
Fix: Projection layer với residual connection


❌ Decoder yếu

Features tốt nhưng decoder không generate well
Check: Decoder architecture gì? Pretrained không?