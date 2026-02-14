from django.core.management.base import BaseCommand
from apps.store.models import ProductCategory, Product


class Command(BaseCommand):
    help = 'Poblar la tienda con productos y categorías iniciales'

    def handle(self, *args, **options):
        # Categorías
        cats = {
            'ropa': ('Ropa', 'fa-tshirt', 1),
            'tazas': ('Tazas', 'fa-coffee', 2),
            'stickers': ('Stickers', 'fa-sticky-note', 3),
            'accesorios': ('Accesorios', 'fa-mouse', 4),
        }
        cat_objs = {}
        for slug, (name, icon, order) in cats.items():
            obj, created = ProductCategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'order': order}
            )
            cat_objs[slug] = obj
            status = 'creada' if created else 'ya existe'
            self.stdout.write(f'  Categoría: {name} ({status})')

        # Productos
        products = [
            {
                'slug': 'camiseta-classic',
                'name': 'Camiseta Megadominio Classic',
                'category': 'ropa',
                'description': 'Algodón 100%, logo bordado. Disponible en negro y blanco.',
                'price': '24.99',
                'icon': 'fa-tshirt',
                'icon_color': 'text-red-500',
                'badge': 'new',
                'stock': 50,
                'is_featured': True,
            },
            {
                'slug': 'hoodie-dev',
                'name': 'Hoodie Dev Mode',
                'category': 'ropa',
                'description': 'Hoodie premium con capucha. Estampado "{ dev_mode: ON }".',
                'price': '49.99',
                'icon': 'fa-code',
                'icon_color': 'text-gray-400',
                'badge': 'popular',
                'stock': 30,
                'is_featured': True,
            },
            {
                'slug': 'gorra-snapback',
                'name': 'Gorra Snapback Mega',
                'category': 'ropa',
                'description': 'Gorra ajustable con logo Megadominio bordado en 3D.',
                'price': '19.99',
                'icon': 'fa-hat-cowboy',
                'icon_color': 'text-blue-400',
                'badge': '',
                'stock': 40,
            },
            {
                'slug': 'taza-console',
                'name': 'Taza console.log("café")',
                'category': 'tazas',
                'description': 'Cerámica 350ml. Diseño minimalista con código real.',
                'price': '14.99',
                'icon': 'fa-mug-hot',
                'icon_color': 'text-amber-400',
                'badge': 'new',
                'stock': 60,
            },
            {
                'slug': 'taza-logo',
                'name': 'Taza Megadominio Logo',
                'category': 'tazas',
                'description': 'Cerámica premium 400ml con logo rojo. "Fuel your code".',
                'price': '12.99',
                'icon': 'fa-coffee',
                'icon_color': 'text-red-500',
                'badge': '',
                'stock': 45,
            },
            {
                'slug': 'termo-deploy',
                'name': 'Termo Deploy Ready',
                'category': 'tazas',
                'description': 'Acero inoxidable 500ml. Mantiene caliente 12h. Tapa hermética.',
                'price': '29.99',
                'icon': 'fa-flask',
                'icon_color': 'text-green-400',
                'badge': '',
                'stock': 25,
            },
            {
                'slug': 'stickers-dev',
                'name': 'Pack Stickers Dev',
                'category': 'stickers',
                'description': '25 stickers de vinilo resistentes al agua. Lenguajes y frameworks.',
                'price': '9.99',
                'icon': 'fa-sticky-note',
                'icon_color': 'text-purple-400',
                'badge': '',
                'stock': 100,
            },
            {
                'slug': 'sticker-logo',
                'name': 'Sticker Megadominio Logo',
                'category': 'stickers',
                'description': 'Sticker holográfico 8cm. Perfecto para laptop o monitor.',
                'price': '3.99',
                'icon': 'fa-certificate',
                'icon_color': 'text-red-400',
                'badge': '',
                'stock': 200,
            },
            {
                'slug': 'mousepad-xl',
                'name': 'Mousepad XL Megadominio',
                'category': 'accesorios',
                'description': '80x30cm, base antideslizante, bordes cosidos. Diseño dark mode.',
                'price': '18.99',
                'icon': 'fa-mouse',
                'icon_color': 'text-cyan-400',
                'badge': 'popular',
                'stock': 35,
                'is_featured': True,
            },
            {
                'slug': 'llavero-usb',
                'name': 'Llavero USB 32GB',
                'category': 'accesorios',
                'description': 'USB 3.0 con forma de llave. Logo Megadominio grabado en metal.',
                'price': '15.99',
                'icon': 'fa-usb',
                'icon_color': 'text-yellow-400',
                'badge': '',
                'stock': 50,
            },
            {
                'slug': 'libreta-dev',
                'name': 'Libreta Dev Notes',
                'category': 'accesorios',
                'description': 'A5, 200 páginas con grid de puntos. Tapa dura con logo.',
                'price': '11.99',
                'icon': 'fa-book',
                'icon_color': 'text-orange-400',
                'badge': '',
                'stock': 40,
            },
            {
                'slug': 'botella-hydrate',
                'name': 'Botella Hydrate.js',
                'category': 'accesorios',
                'description': '750ml, tritán BPA-free. Grabado "Stay hydrated, keep coding".',
                'price': '16.99',
                'icon': 'fa-wine-bottle',
                'icon_color': 'text-teal-400',
                'badge': '',
                'stock': 30,
            },
        ]

        for p in products:
            cat_slug = p.pop('category')
            obj, created = Product.objects.get_or_create(
                slug=p['slug'],
                defaults={
                    **p,
                    'category': cat_objs[cat_slug],
                }
            )
            status = 'creado' if created else 'ya existe'
            self.stdout.write(f'  Producto: {obj.name} ({status})')

        self.stdout.write(self.style.SUCCESS(
            f'\nListo: {len(cats)} categorías, {len(products)} productos.'
        ))
