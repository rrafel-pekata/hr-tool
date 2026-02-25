from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from apps.tenants.models import Company, CompanyMembership

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un usuario y lo asocia a una empresa con un rol (recruiter por defecto).'

    def add_arguments(self, parser):
        parser.add_argument('email', help='Email del usuario (se usa también como username)')
        parser.add_argument('--first-name', default='', help='Nombre')
        parser.add_argument('--last-name', default='', help='Apellidos')
        parser.add_argument('--password', help='Contraseña (si no se indica, se pide de forma interactiva)')
        parser.add_argument('--company', help='Slug o nombre de la empresa')
        parser.add_argument(
            '--role',
            choices=[r.value for r in CompanyMembership.Role],
            default=CompanyMembership.Role.RECRUITER,
            help='Rol en la empresa (default: recruiter)',
        )

    def handle(self, *args, **options):
        email = options['email']

        if User.objects.filter(username=email).exists():
            raise CommandError(f'Ya existe un usuario con username "{email}".')

        # Contraseña
        password = options.get('password')
        if not password:
            import getpass
            password = getpass.getpass('Contraseña: ')
            password2 = getpass.getpass('Repite contraseña: ')
            if password != password2:
                raise CommandError('Las contraseñas no coinciden.')

        # Empresa
        company = self._resolve_company(options.get('company'))

        # Crear usuario
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=options['first_name'],
            last_name=options['last_name'],
        )

        # Crear membresía
        role = options['role']
        CompanyMembership.objects.create(user=user, company=company, role=role)

        self.stdout.write(self.style.SUCCESS(
            f'Usuario "{email}" creado con rol "{role}" en "{company.name}".'
        ))

    def _resolve_company(self, company_hint):
        companies = Company.objects.all()
        if not companies.exists():
            raise CommandError('No hay empresas creadas. Crea una primero.')

        if company_hint:
            try:
                return companies.get(slug=company_hint)
            except Company.DoesNotExist:
                try:
                    return companies.get(name__iexact=company_hint)
                except Company.DoesNotExist:
                    raise CommandError(f'No se encontró la empresa "{company_hint}".')

        if companies.count() == 1:
            return companies.first()

        # Varias empresas: mostrar listado y pedir selección
        self.stdout.write('Empresas disponibles:')
        company_list = list(companies)
        for i, c in enumerate(company_list, 1):
            self.stdout.write(f'  {i}. {c.name} ({c.slug})')

        choice = input('Selecciona empresa (número): ')
        try:
            return company_list[int(choice) - 1]
        except (ValueError, IndexError):
            raise CommandError('Selección no válida.')
