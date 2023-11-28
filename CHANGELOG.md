# Changelog

<!--next-version-placeholder-->

## v1.2.3 (2022-12-01)
### Fix
* **submodule:** Arcimoto-aws-services version 1.1.7 release ([`c8102f1`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/c8102f116f8d11e0a51ae322d994faeca957a819))

## v1.2.2 (2022-11-17)
### Fix
* **pipeline:** Back-merge for new release publish ([`30a7ec5`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/30a7ec5b0fa21f135d8046727a5178179922957f))

## v1.2.1 (2022-11-16)
### Fix
* **pipeline:** Get chnagelog for prod release email from git ([`2e9ebb6`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/2e9ebb6cd11202c61cc9e0a350d32a46d5a5a2a1))

## v1.2.0 (2022-11-16)
### Feature
* Bring in arcimoto-aws-services upstream changes ([`0932e71`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/0932e713e08042da77c9fc27471aa49c3134a896))
* **submodule:** Point to ses branch ([`912517c`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/912517cc33e0478f01c6421ca534a7eb9ca907a0))
* Create ses utility, remove unused files ([`00c4faa`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/00c4faa5e46ab3726e0c7fc3dbd1083ba560fb30))

### Fix
* **template_upsert:** Pass mute to library ([`7a75589`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/7a7558953dc28e3d1f838dd4175e672339ef305d))

### Documentation
* Update readmes ([`e1a5408`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/e1a5408bc185da07537037babf65a19576292b23))

## v1.1.1 (2022-11-08)
### Fix
* **requirements:** Add missing dependency boto3 ([`e902e6a`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/e902e6ac19cf879bb69d32d4a6d3f9018c1a3822))
* **command:release:** Handle too many requests exception in release_prod ([`748ef3c`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/748ef3cf05c222f597ba12a3bad204702d629eab))

## v1.1.0 (2022-11-01)
### Feature
* **pipeline:** Setup caching for all steps ([`02780eb`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/02780ebac2ca741d72811e7ac0bfa3dd0b0da867))

## v1.0.0 (2022-10-28)


## v0.1.0 (2022-10-28)
### Feature
* Add automatic semantic versioning and changelog ([`7fcec47`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/7fcec473c588395d21fe74292faf17d8c2b47b6b))
* **lambda service:** Add lambda_exists function ([`6a2622f`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/6a2622ffd900b32cd4f52c6d79799c1f712a3ccb))
* **command:test:** Honor mute, etc ([`206c4f2`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/206c4f28a57f5a2db9c776f7aceb5ea8c3284a86))
* **lambda service:** Add LambdaTestArgs class ([`4c5f923`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/4c5f923e94b68d2c80e0f5f0e63e137a8c2b6340))
* **lambda service:** Add lambda_update_code ([`b35f493`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/b35f493b02375c24dba875a22377255f7f4a4d32))

### Fix
* **git:** Change submodule url to use git protocol ([`9c4633d`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/9c4633d0e89cbdea9a316e8dae5c2521b8eb0172))
* **pipeline:** Change submodule init command ([`fe21ddd`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/fe21dddf97621cf213615a82330214e709bf0c14))
* **pipeline:** Add git sub module update ([`2fa9784`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/2fa97846820df6b015a11a66d15b6f1f86b2d99e))
* **pipeline:** Add git sub module init ([`6f81050`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/6f81050991563d2a7661b84e5ae8f33cba27b803))
* **lambda service:** Handle region only in base class ([`1eaa362`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/1eaa362816f11bcdcad6b10614e84246ad0e3733))
* **aws service:** Set the initial region in base class ([`899ec97`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/899ec978de6a99bfc72b534933b35ca71531e3c0))
* **command:test:** Final cleanup ([`46d4e43`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/46d4e431069833e7945c36b4aa236e336442dc4a))
* **command:test:** Finalize refactoring and minor bug fixes ([`577ff05`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/577ff0506a2023a5d324dcf9f8bfb7db20f32926))
* **command:test:** Output xml for all test results, not just first ([`289f9c0`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/289f9c0b9105227d7d7706cb766031eda6ad1944))
* **lambda service:** Re-add LambdaRuntimeArgs ([`29d19e8`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/29d19e8a55e7fd77c568b5143f4c33c8eb2411f7))
* **command:layer:** Revert change to re-setup object ([`1ad18d5`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/1ad18d5a6ea5390816a46cad31e61dc3beb9fdf5))
* **command:grant_api:** Remove left over object set up ([`5295bad`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/5295badeaaf7ab81d3695933be06971ef978a915))
* **command:** Honor region input ([`9a5669c`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/9a5669cc7a2828b9610e47e79b2973f2380f6007))
* **command:update:** Honor mute for log statements ([`ec6ce3f`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/ec6ce3ff70df4dd1f5c6607db540f596e7c63b00))
* **lambda service:** Mute logger statement ([`ff4a639`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/ff4a639263e852def237e7a01636c03357331708))

### Documentation
* **readme:** Include info about usage in pipeline via ssh ([`c2dc035`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/c2dc035fc687c5186a7c0da7d07dcbc7aebca3f6))
* Update readme ([`5bd4395`](https://github.com/arcimotocode1/arcimoto-lambda-utility/commit/5bd4395d6569b3b3e92c8898e585c53d2e02d3d3))
