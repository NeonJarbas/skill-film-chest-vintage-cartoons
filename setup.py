#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-film-chest-vintage-cartoons.jarbasai=skill_film_chest_vintage_cartoons:FilmChestVintageCartoonsSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-film-chest-vintage-cartoons',
    version='0.0.1',
    description='ovos FilmChestVintageCartoons skill plugin',
    url='https://github.com/JarbasSkills/skill-film-chest-vintage-cartoons',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_film_chest_vintage_cartoons": ""},
    package_data={'skill_film_chest_vintage_cartoons': ['locale/*', 'ui/*']},
    packages=['skill_film_chest_vintage_cartoons'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
