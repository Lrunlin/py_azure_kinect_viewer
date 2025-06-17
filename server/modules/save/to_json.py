def save_point_cloud_json(points, colors):
    data = []
    for i in range(points.shape[0]):
        x, y, z = points[i]
        r, g, b = colors[i]
        data.append({
            "x": float(x),
            "y": float(y),
            "z": float(z),
            "r": int(r),
            "g": int(g),
            "b": int(b)
        })
    return data
