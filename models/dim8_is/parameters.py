# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.0.1 for Linux x86 (64-bit) (January 29, 2022)
# Date: Mon 7 Sep 2026 00:36:41



from object_library import all_parameters, Parameter


from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
cabi = Parameter(name = 'cabi',
                 nature = 'external',
                 type = 'real',
                 value = 0.227736,
                 texname = '\\theta _c',
                 lhablock = 'CKMBLOCK',
                 lhacode = [ 1 ])

Lam6 = Parameter(name = 'Lam6',
                 nature = 'external',
                 type = 'real',
                 value = 1000,
                 texname = '\\text{Lam6}',
                 lhablock = 'DIM6',
                 lhacode = [ 1 ])

cHW = Parameter(name = 'cHW',
                nature = 'external',
                type = 'real',
                value = 0,
                texname = '\\text{cHW}',
                lhablock = 'DIM6',
                lhacode = [ 2 ])

cHB = Parameter(name = 'cHB',
                nature = 'external',
                type = 'real',
                value = 0,
                texname = '\\text{cHB}',
                lhablock = 'DIM6',
                lhacode = [ 3 ])

cHWB = Parameter(name = 'cHWB',
                 nature = 'external',
                 type = 'real',
                 value = 0,
                 texname = '\\text{cHWB}',
                 lhablock = 'DIM6',
                 lhacode = [ 4 ])

cHDD = Parameter(name = 'cHDD',
                 nature = 'external',
                 type = 'real',
                 value = 0,
                 texname = '\\text{cHDD}',
                 lhablock = 'DIM6',
                 lhacode = [ 5 ])

cHl3 = Parameter(name = 'cHl3',
                 nature = 'external',
                 type = 'real',
                 value = 0,
                 texname = '\\text{cHl3}',
                 lhablock = 'DIM6',
                 lhacode = [ 6 ])

cll1 = Parameter(name = 'cll1',
                 nature = 'external',
                 type = 'real',
                 value = 0,
                 texname = '\\text{cll1}',
                 lhablock = 'DIM6',
                 lhacode = [ 7 ])

cHbox = Parameter(name = 'cHbox',
                  nature = 'external',
                  type = 'real',
                  value = 0,
                  texname = '\\text{cHbox}',
                  lhablock = 'DIM6',
                  lhacode = [ 8 ])

cH = Parameter(name = 'cH',
               nature = 'external',
               type = 'real',
               value = 0,
               texname = '\\text{cH}',
               lhablock = 'DIM6',
               lhacode = [ 9 ])

Lam = Parameter(name = 'Lam',
                nature = 'external',
                type = 'real',
                value = 1000.,
                texname = '\\Lambda',
                lhablock = 'DIM8',
                lhacode = [ 0 ])

c8leWH3x1Re = Parameter(name = 'c8leWH3x1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWH3x1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 1 ])

c8leWH3x1Im = Parameter(name = 'c8leWH3x1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWH3x1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 2 ])

c8leWH3x2Re = Parameter(name = 'c8leWH3x2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWH3x2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 3 ])

c8leWH3x2Im = Parameter(name = 'c8leWH3x2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWH3x2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 4 ])

c8leBH3Re = Parameter(name = 'c8leBH3Re',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8leBH3Re}',
                      lhablock = 'DIM8',
                      lhacode = [ 5 ])

c8leBH3Im = Parameter(name = 'c8leBH3Im',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8leBH3Im}',
                      lhablock = 'DIM8',
                      lhacode = [ 6 ])

c8quGH3Re = Parameter(name = 'c8quGH3Re',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8quGH3Re}',
                      lhablock = 'DIM8',
                      lhacode = [ 7 ])

c8quGH3Im = Parameter(name = 'c8quGH3Im',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8quGH3Im}',
                      lhablock = 'DIM8',
                      lhacode = [ 8 ])

c8quWH3x1Re = Parameter(name = 'c8quWH3x1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWH3x1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 9 ])

c8quWH3x1Im = Parameter(name = 'c8quWH3x1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWH3x1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 10 ])

c8quWH3x2Re = Parameter(name = 'c8quWH3x2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWH3x2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 11 ])

c8quWH3x2Im = Parameter(name = 'c8quWH3x2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWH3x2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 12 ])

c8quBH3Re = Parameter(name = 'c8quBH3Re',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8quBH3Re}',
                      lhablock = 'DIM8',
                      lhacode = [ 13 ])

c8quBH3Im = Parameter(name = 'c8quBH3Im',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8quBH3Im}',
                      lhablock = 'DIM8',
                      lhacode = [ 14 ])

c8qdGH3Re = Parameter(name = 'c8qdGH3Re',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8qdGH3Re}',
                      lhablock = 'DIM8',
                      lhacode = [ 15 ])

c8qdGH3Im = Parameter(name = 'c8qdGH3Im',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8qdGH3Im}',
                      lhablock = 'DIM8',
                      lhacode = [ 16 ])

c8qdWH3x1Re = Parameter(name = 'c8qdWH3x1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWH3x1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 17 ])

c8qdWH3x1Im = Parameter(name = 'c8qdWH3x1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWH3x1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 18 ])

c8qdWH3x2Re = Parameter(name = 'c8qdWH3x2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWH3x2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 19 ])

c8qdWH3x2Im = Parameter(name = 'c8qdWH3x2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWH3x2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 20 ])

c8qdBH3Re = Parameter(name = 'c8qdBH3Re',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8qdBH3Re}',
                      lhablock = 'DIM8',
                      lhacode = [ 21 ])

c8qdBH3Im = Parameter(name = 'c8qdBH3Im',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8qdBH3Im}',
                      lhablock = 'DIM8',
                      lhacode = [ 22 ])

c8l2H2D3x1 = Parameter(name = 'c8l2H2D3x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2H2D3x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 23 ])

c8l2H2D3x2 = Parameter(name = 'c8l2H2D3x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2H2D3x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 24 ])

c8l2H2D3x3 = Parameter(name = 'c8l2H2D3x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2H2D3x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 25 ])

c8l2H2D3x4 = Parameter(name = 'c8l2H2D3x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2H2D3x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 26 ])

c8e2H2D3x1 = Parameter(name = 'c8e2H2D3x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2H2D3x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 27 ])

c8e2H2D3x2 = Parameter(name = 'c8e2H2D3x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2H2D3x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 28 ])

c8q2H2D3x1 = Parameter(name = 'c8q2H2D3x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2H2D3x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 29 ])

c8q2H2D3x2 = Parameter(name = 'c8q2H2D3x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2H2D3x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 30 ])

c8q2H2D3x3 = Parameter(name = 'c8q2H2D3x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2H2D3x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 31 ])

c8q2H2D3x4 = Parameter(name = 'c8q2H2D3x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2H2D3x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 32 ])

c8u2H2D3x1 = Parameter(name = 'c8u2H2D3x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2H2D3x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 33 ])

c8u2H2D3x2 = Parameter(name = 'c8u2H2D3x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2H2D3x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 34 ])

c8d2H2D3x1 = Parameter(name = 'c8d2H2D3x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2H2D3x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 35 ])

c8d2H2D3x2 = Parameter(name = 'c8d2H2D3x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2H2D3x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 36 ])

c8udH2D3Re = Parameter(name = 'c8udH2D3Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8udH2D3Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 37 ])

c8udH2D3Im = Parameter(name = 'c8udH2D3Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8udH2D3Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 38 ])

c8leH5Re = Parameter(name = 'c8leH5Re',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = '\\text{c8leH5Re}',
                     lhablock = 'DIM8',
                     lhacode = [ 39 ])

c8leH5Im = Parameter(name = 'c8leH5Im',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = '\\text{c8leH5Im}',
                     lhablock = 'DIM8',
                     lhacode = [ 40 ])

c8quH5Re = Parameter(name = 'c8quH5Re',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = '\\text{c8quH5Re}',
                     lhablock = 'DIM8',
                     lhacode = [ 41 ])

c8quH5Im = Parameter(name = 'c8quH5Im',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = '\\text{c8quH5Im}',
                     lhablock = 'DIM8',
                     lhacode = [ 42 ])

c8qdH5Re = Parameter(name = 'c8qdH5Re',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = '\\text{c8qdH5Re}',
                     lhablock = 'DIM8',
                     lhacode = [ 43 ])

c8qdH5Im = Parameter(name = 'c8qdH5Im',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = '\\text{c8qdH5Im}',
                     lhablock = 'DIM8',
                     lhacode = [ 44 ])

c8l2H4Dx1 = Parameter(name = 'c8l2H4Dx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2H4Dx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 45 ])

c8l2H4Dx2 = Parameter(name = 'c8l2H4Dx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2H4Dx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 46 ])

c8l2H4Dx3 = Parameter(name = 'c8l2H4Dx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2H4Dx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 47 ])

c8l2H4Dx4 = Parameter(name = 'c8l2H4Dx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2H4Dx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 48 ])

c8e2H4D = Parameter(name = 'c8e2H4D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{e2H4D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 49 ])

c8q2H4Dx1 = Parameter(name = 'c8q2H4Dx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2H4Dx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 50 ])

c8q2H4Dx2 = Parameter(name = 'c8q2H4Dx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2H4Dx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 51 ])

c8q2H4Dx3 = Parameter(name = 'c8q2H4Dx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2H4Dx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 52 ])

c8q2H4Dx4 = Parameter(name = 'c8q2H4Dx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2H4Dx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 53 ])

c8u2H4D = Parameter(name = 'c8u2H4D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{u2H4D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 54 ])

c8d2H4D = Parameter(name = 'c8d2H4D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{d2H4D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 55 ])

c8udH4DRe = Parameter(name = 'c8udH4DRe',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8udH4DRe}',
                      lhablock = 'DIM8',
                      lhacode = [ 56 ])

c8udH4DIm = Parameter(name = 'c8udH4DIm',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8udH4DIm}',
                      lhablock = 'DIM8',
                      lhacode = [ 57 ])

c8q2G2Dx1 = Parameter(name = 'c8q2G2Dx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2G2Dx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 58 ])

c8q2G2Dx2 = Parameter(name = 'c8q2G2Dx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2G2Dx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 59 ])

c8q2G2Dx3 = Parameter(name = 'c8q2G2Dx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2G2Dx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 60 ])

c8q2W2Dx1 = Parameter(name = 'c8q2W2Dx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2W2Dx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 61 ])

c8q2W2Dx2 = Parameter(name = 'c8q2W2Dx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2W2Dx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 62 ])

c8q2B2D = Parameter(name = 'c8q2B2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q2B2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 63 ])

c8u2G2Dx1 = Parameter(name = 'c8u2G2Dx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2G2Dx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 64 ])

c8u2G2Dx2 = Parameter(name = 'c8u2G2Dx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2G2Dx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 65 ])

c8u2G2Dx3 = Parameter(name = 'c8u2G2Dx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2G2Dx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 66 ])

c8u2W2D = Parameter(name = 'c8u2W2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{u2W2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 67 ])

c8u2B2D = Parameter(name = 'c8u2B2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{u2B2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 68 ])

c8d2G2Dx1 = Parameter(name = 'c8d2G2Dx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2G2Dx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 69 ])

c8d2G2Dx2 = Parameter(name = 'c8d2G2Dx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2G2Dx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 70 ])

c8d2G2Dx3 = Parameter(name = 'c8d2G2Dx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2G2Dx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 71 ])

c8d2W2D = Parameter(name = 'c8d2W2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{d2W2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 72 ])

c8d2B2D = Parameter(name = 'c8d2B2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{d2B2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 73 ])

c8q2G2Dx4 = Parameter(name = 'c8q2G2Dx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2G2Dx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 74 ])

c8q2G2Dx5 = Parameter(name = 'c8q2G2Dx5',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2G2Dx5}}',
                      lhablock = 'DIM8',
                      lhacode = [ 75 ])

c8q2GWDx1 = Parameter(name = 'c8q2GWDx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2GWDx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 76 ])

c8q2GWDx2 = Parameter(name = 'c8q2GWDx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2GWDx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 77 ])

c8q2GWDx3 = Parameter(name = 'c8q2GWDx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2GWDx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 78 ])

c8q2GWDx4 = Parameter(name = 'c8q2GWDx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2GWDx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 79 ])

c8q2GBDx1 = Parameter(name = 'c8q2GBDx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2GBDx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 80 ])

c8q2GBDx2 = Parameter(name = 'c8q2GBDx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2GBDx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 81 ])

c8q2GBDx3 = Parameter(name = 'c8q2GBDx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2GBDx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 82 ])

c8q2GBDx4 = Parameter(name = 'c8q2GBDx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2GBDx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 83 ])

c8q2W2Dx3 = Parameter(name = 'c8q2W2Dx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2W2Dx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 84 ])

c8q2W2Dx4 = Parameter(name = 'c8q2W2Dx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2W2Dx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 85 ])

c8q2WBDx1 = Parameter(name = 'c8q2WBDx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2WBDx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 86 ])

c8q2WBDx2 = Parameter(name = 'c8q2WBDx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2WBDx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 87 ])

c8q2WBDx3 = Parameter(name = 'c8q2WBDx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2WBDx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 88 ])

c8q2WBDx4 = Parameter(name = 'c8q2WBDx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2WBDx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 89 ])

c8u2G2Dx4 = Parameter(name = 'c8u2G2Dx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2G2Dx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 90 ])

c8u2G2Dx5 = Parameter(name = 'c8u2G2Dx5',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2G2Dx5}}',
                      lhablock = 'DIM8',
                      lhacode = [ 91 ])

c8u2GBDx1 = Parameter(name = 'c8u2GBDx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2GBDx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 92 ])

c8u2GBDx2 = Parameter(name = 'c8u2GBDx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2GBDx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 93 ])

c8u2GBDx3 = Parameter(name = 'c8u2GBDx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2GBDx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 94 ])

c8u2GBDx4 = Parameter(name = 'c8u2GBDx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2GBDx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 95 ])

c8d2G2Dx4 = Parameter(name = 'c8d2G2Dx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2G2Dx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 96 ])

c8d2G2Dx5 = Parameter(name = 'c8d2G2Dx5',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2G2Dx5}}',
                      lhablock = 'DIM8',
                      lhacode = [ 97 ])

c8d2GBDx1 = Parameter(name = 'c8d2GBDx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2GBDx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 98 ])

c8d2GBDx2 = Parameter(name = 'c8d2GBDx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2GBDx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 99 ])

c8d2GBDx3 = Parameter(name = 'c8d2GBDx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2GBDx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 100 ])

c8d2GBDx4 = Parameter(name = 'c8d2GBDx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{d2GBDx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 101 ])

c8l2G2D = Parameter(name = 'c8l2G2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{l2G2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 102 ])

c8l2W2Dx1 = Parameter(name = 'c8l2W2Dx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2W2Dx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 103 ])

c8l2W2Dx2 = Parameter(name = 'c8l2W2Dx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2W2Dx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 104 ])

c8l2B2D = Parameter(name = 'c8l2B2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{l2B2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 105 ])

c8e2G2D = Parameter(name = 'c8e2G2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{e2G2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 106 ])

c8e2W2D = Parameter(name = 'c8e2W2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{e2W2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 107 ])

c8e2B2D = Parameter(name = 'c8e2B2D',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{e2B2D}}',
                    lhablock = 'DIM8',
                    lhacode = [ 108 ])

c8l2W2Dx3 = Parameter(name = 'c8l2W2Dx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2W2Dx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 109 ])

c8l2W2Dx4 = Parameter(name = 'c8l2W2Dx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2W2Dx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 110 ])

c8l2WBDx1 = Parameter(name = 'c8l2WBDx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2WBDx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 111 ])

c8l2WBDx2 = Parameter(name = 'c8l2WBDx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2WBDx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 112 ])

c8l2WBDx3 = Parameter(name = 'c8l2WBDx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2WBDx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 113 ])

c8l2WBDx4 = Parameter(name = 'c8l2WBDx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2WBDx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 114 ])

c8e2WH2Dx1 = Parameter(name = 'c8e2WH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2WH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 115 ])

c8e2WH2Dx2 = Parameter(name = 'c8e2WH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2WH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 116 ])

c8e2WH2Dx3 = Parameter(name = 'c8e2WH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2WH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 117 ])

c8e2WH2Dx4 = Parameter(name = 'c8e2WH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2WH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 118 ])

c8e2BH2Dx1 = Parameter(name = 'c8e2BH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2BH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 119 ])

c8e2BH2Dx2 = Parameter(name = 'c8e2BH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2BH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 120 ])

c8e2BH2Dx3 = Parameter(name = 'c8e2BH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2BH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 121 ])

c8e2BH2Dx4 = Parameter(name = 'c8e2BH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2BH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 122 ])

c8u2GH2Dx1 = Parameter(name = 'c8u2GH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2GH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 123 ])

c8u2GH2Dx2 = Parameter(name = 'c8u2GH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2GH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 124 ])

c8u2GH2Dx3 = Parameter(name = 'c8u2GH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2GH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 125 ])

c8u2GH2Dx4 = Parameter(name = 'c8u2GH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2GH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 126 ])

c8u2WH2Dx1 = Parameter(name = 'c8u2WH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2WH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 127 ])

c8u2WH2Dx2 = Parameter(name = 'c8u2WH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2WH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 128 ])

c8u2WH2Dx3 = Parameter(name = 'c8u2WH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2WH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 129 ])

c8u2WH2Dx4 = Parameter(name = 'c8u2WH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2WH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 130 ])

c8u2BH2Dx1 = Parameter(name = 'c8u2BH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2BH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 131 ])

c8u2BH2Dx2 = Parameter(name = 'c8u2BH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2BH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 132 ])

c8u2BH2Dx3 = Parameter(name = 'c8u2BH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2BH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 133 ])

c8u2BH2Dx4 = Parameter(name = 'c8u2BH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2BH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 134 ])

c8d2GH2Dx1 = Parameter(name = 'c8d2GH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2GH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 135 ])

c8d2GH2Dx2 = Parameter(name = 'c8d2GH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2GH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 136 ])

c8d2GH2Dx3 = Parameter(name = 'c8d2GH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2GH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 137 ])

c8d2GH2Dx4 = Parameter(name = 'c8d2GH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2GH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 138 ])

c8d2WH2Dx1 = Parameter(name = 'c8d2WH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2WH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 139 ])

c8d2WH2Dx2 = Parameter(name = 'c8d2WH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2WH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 140 ])

c8d2WH2Dx3 = Parameter(name = 'c8d2WH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2WH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 141 ])

c8d2WH2Dx4 = Parameter(name = 'c8d2WH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2WH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 142 ])

c8d2BH2Dx1 = Parameter(name = 'c8d2BH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2BH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 143 ])

c8d2BH2Dx2 = Parameter(name = 'c8d2BH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2BH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 144 ])

c8d2BH2Dx3 = Parameter(name = 'c8d2BH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2BH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 145 ])

c8d2BH2Dx4 = Parameter(name = 'c8d2BH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{d2BH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 146 ])

c8udGH2x1Re = Parameter(name = 'c8udGH2x1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udGH2x1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 147 ])

c8udGH2x1Im = Parameter(name = 'c8udGH2x1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udGH2x1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 148 ])

c8udGH2x2Re = Parameter(name = 'c8udGH2x2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udGH2x2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 149 ])

c8udGH2x2Im = Parameter(name = 'c8udGH2x2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udGH2x2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 150 ])

c8udWH2x1Re = Parameter(name = 'c8udWH2x1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udWH2x1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 151 ])

c8udWH2x1Im = Parameter(name = 'c8udWH2x1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udWH2x1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 152 ])

c8udWH2x2Re = Parameter(name = 'c8udWH2x2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udWH2x2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 153 ])

c8udWH2x2Im = Parameter(name = 'c8udWH2x2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udWH2x2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 154 ])

c8udBH2x1Re = Parameter(name = 'c8udBH2x1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udBH2x1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 155 ])

c8udBH2x1Im = Parameter(name = 'c8udBH2x1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udBH2x1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 156 ])

c8udBH2x2Re = Parameter(name = 'c8udBH2x2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udBH2x2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 157 ])

c8udBH2x2Im = Parameter(name = 'c8udBH2x2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8udBH2x2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 158 ])

c8l2WH2Dx1 = Parameter(name = 'c8l2WH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 159 ])

c8l2WH2Dx2 = Parameter(name = 'c8l2WH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 160 ])

c8l2WH2Dx3 = Parameter(name = 'c8l2WH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 161 ])

c8l2WH2Dx4 = Parameter(name = 'c8l2WH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 162 ])

c8l2WH2Dx5 = Parameter(name = 'c8l2WH2Dx5',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx5}}',
                       lhablock = 'DIM8',
                       lhacode = [ 163 ])

c8l2WH2Dx6 = Parameter(name = 'c8l2WH2Dx6',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx6}}',
                       lhablock = 'DIM8',
                       lhacode = [ 164 ])

c8l2WH2Dx7 = Parameter(name = 'c8l2WH2Dx7',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx7}}',
                       lhablock = 'DIM8',
                       lhacode = [ 165 ])

c8l2WH2Dx8 = Parameter(name = 'c8l2WH2Dx8',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx8}}',
                       lhablock = 'DIM8',
                       lhacode = [ 166 ])

c8l2WH2Dx9 = Parameter(name = 'c8l2WH2Dx9',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2WH2Dx9}}',
                       lhablock = 'DIM8',
                       lhacode = [ 167 ])

c8l2WH2Dx10 = Parameter(name = 'c8l2WH2Dx10',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = 'c_{8 \\text{l2WH2Dx10}}',
                        lhablock = 'DIM8',
                        lhacode = [ 168 ])

c8l2WH2Dx11 = Parameter(name = 'c8l2WH2Dx11',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = 'c_{8 \\text{l2WH2Dx11}}',
                        lhablock = 'DIM8',
                        lhacode = [ 169 ])

c8l2WH2Dx12 = Parameter(name = 'c8l2WH2Dx12',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = 'c_{8 \\text{l2WH2Dx12}}',
                        lhablock = 'DIM8',
                        lhacode = [ 170 ])

c8l2BH2Dx1 = Parameter(name = 'c8l2BH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2BH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 171 ])

c8l2BH2Dx2 = Parameter(name = 'c8l2BH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2BH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 172 ])

c8l2BH2Dx3 = Parameter(name = 'c8l2BH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2BH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 173 ])

c8l2BH2Dx4 = Parameter(name = 'c8l2BH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2BH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 174 ])

c8l2BH2Dx5 = Parameter(name = 'c8l2BH2Dx5',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2BH2Dx5}}',
                       lhablock = 'DIM8',
                       lhacode = [ 175 ])

c8l2BH2Dx6 = Parameter(name = 'c8l2BH2Dx6',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2BH2Dx6}}',
                       lhablock = 'DIM8',
                       lhacode = [ 176 ])

c8l2BH2Dx7 = Parameter(name = 'c8l2BH2Dx7',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2BH2Dx7}}',
                       lhablock = 'DIM8',
                       lhacode = [ 177 ])

c8l2BH2Dx8 = Parameter(name = 'c8l2BH2Dx8',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2BH2Dx8}}',
                       lhablock = 'DIM8',
                       lhacode = [ 178 ])

c8q2GH2Dx1 = Parameter(name = 'c8q2GH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2GH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 179 ])

c8q2GH2Dx2 = Parameter(name = 'c8q2GH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2GH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 180 ])

c8q2GH2Dx3 = Parameter(name = 'c8q2GH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2GH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 181 ])

c8q2GH2Dx4 = Parameter(name = 'c8q2GH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2GH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 182 ])

c8q2GH2Dx5 = Parameter(name = 'c8q2GH2Dx5',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2GH2Dx5}}',
                       lhablock = 'DIM8',
                       lhacode = [ 183 ])

c8q2GH2Dx6 = Parameter(name = 'c8q2GH2Dx6',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2GH2Dx6}}',
                       lhablock = 'DIM8',
                       lhacode = [ 184 ])

c8q2GH2Dx7 = Parameter(name = 'c8q2GH2Dx7',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2GH2Dx7}}',
                       lhablock = 'DIM8',
                       lhacode = [ 185 ])

c8q2GH2Dx8 = Parameter(name = 'c8q2GH2Dx8',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2GH2Dx8}}',
                       lhablock = 'DIM8',
                       lhacode = [ 186 ])

c8q2WH2Dx1 = Parameter(name = 'c8q2WH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 187 ])

c8q2WH2Dx2 = Parameter(name = 'c8q2WH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 188 ])

c8q2WH2Dx3 = Parameter(name = 'c8q2WH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 189 ])

c8q2WH2Dx4 = Parameter(name = 'c8q2WH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 190 ])

c8q2WH2Dx5 = Parameter(name = 'c8q2WH2Dx5',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx5}}',
                       lhablock = 'DIM8',
                       lhacode = [ 191 ])

c8q2WH2Dx6 = Parameter(name = 'c8q2WH2Dx6',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx6}}',
                       lhablock = 'DIM8',
                       lhacode = [ 192 ])

c8q2WH2Dx7 = Parameter(name = 'c8q2WH2Dx7',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx7}}',
                       lhablock = 'DIM8',
                       lhacode = [ 193 ])

c8q2WH2Dx8 = Parameter(name = 'c8q2WH2Dx8',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx8}}',
                       lhablock = 'DIM8',
                       lhacode = [ 194 ])

c8q2WH2Dx9 = Parameter(name = 'c8q2WH2Dx9',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2WH2Dx9}}',
                       lhablock = 'DIM8',
                       lhacode = [ 195 ])

c8q2WH2Dx10 = Parameter(name = 'c8q2WH2Dx10',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = 'c_{8 \\text{q2WH2Dx10}}',
                        lhablock = 'DIM8',
                        lhacode = [ 196 ])

c8q2WH2Dx11 = Parameter(name = 'c8q2WH2Dx11',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = 'c_{8 \\text{q2WH2Dx11}}',
                        lhablock = 'DIM8',
                        lhacode = [ 197 ])

c8q2WH2Dx12 = Parameter(name = 'c8q2WH2Dx12',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = 'c_{8 \\text{q2WH2Dx12}}',
                        lhablock = 'DIM8',
                        lhacode = [ 198 ])

c8q2BH2Dx1 = Parameter(name = 'c8q2BH2Dx1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2BH2Dx1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 199 ])

c8q2BH2Dx2 = Parameter(name = 'c8q2BH2Dx2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2BH2Dx2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 200 ])

c8q2BH2Dx3 = Parameter(name = 'c8q2BH2Dx3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2BH2Dx3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 201 ])

c8q2BH2Dx4 = Parameter(name = 'c8q2BH2Dx4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2BH2Dx4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 202 ])

c8q2BH2Dx5 = Parameter(name = 'c8q2BH2Dx5',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2BH2Dx5}}',
                       lhablock = 'DIM8',
                       lhacode = [ 203 ])

c8q2BH2Dx6 = Parameter(name = 'c8q2BH2Dx6',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2BH2Dx6}}',
                       lhablock = 'DIM8',
                       lhacode = [ 204 ])

c8q2BH2Dx7 = Parameter(name = 'c8q2BH2Dx7',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2BH2Dx7}}',
                       lhablock = 'DIM8',
                       lhacode = [ 205 ])

c8q2BH2Dx8 = Parameter(name = 'c8q2BH2Dx8',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2BH2Dx8}}',
                       lhablock = 'DIM8',
                       lhacode = [ 206 ])

c8leWHD2x1Re = Parameter(name = 'c8leWHD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leWHD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 207 ])

c8leWHD2x1Im = Parameter(name = 'c8leWHD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leWHD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 208 ])

c8leWHD2x2Re = Parameter(name = 'c8leWHD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leWHD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 209 ])

c8leWHD2x2Im = Parameter(name = 'c8leWHD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leWHD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 210 ])

c8leWHD2x3Re = Parameter(name = 'c8leWHD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leWHD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 211 ])

c8leWHD2x3Im = Parameter(name = 'c8leWHD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leWHD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 212 ])

c8leBHD2x1Re = Parameter(name = 'c8leBHD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leBHD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 213 ])

c8leBHD2x1Im = Parameter(name = 'c8leBHD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leBHD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 214 ])

c8leBHD2x2Re = Parameter(name = 'c8leBHD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leBHD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 215 ])

c8leBHD2x2Im = Parameter(name = 'c8leBHD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leBHD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 216 ])

c8leBHD2x3Re = Parameter(name = 'c8leBHD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leBHD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 217 ])

c8leBHD2x3Im = Parameter(name = 'c8leBHD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leBHD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 218 ])

c8quGHD2x1Re = Parameter(name = 'c8quGHD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quGHD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 219 ])

c8quGHD2x1Im = Parameter(name = 'c8quGHD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quGHD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 220 ])

c8quGHD2x2Re = Parameter(name = 'c8quGHD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quGHD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 221 ])

c8quGHD2x2Im = Parameter(name = 'c8quGHD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quGHD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 222 ])

c8quGHD2x3Re = Parameter(name = 'c8quGHD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quGHD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 223 ])

c8quGHD2x3Im = Parameter(name = 'c8quGHD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quGHD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 224 ])

c8quWHD2x1Re = Parameter(name = 'c8quWHD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quWHD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 225 ])

c8quWHD2x1Im = Parameter(name = 'c8quWHD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quWHD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 226 ])

c8quWHD2x2Re = Parameter(name = 'c8quWHD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quWHD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 227 ])

c8quWHD2x2Im = Parameter(name = 'c8quWHD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quWHD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 228 ])

c8quWHD2x3Re = Parameter(name = 'c8quWHD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quWHD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 229 ])

c8quWHD2x3Im = Parameter(name = 'c8quWHD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quWHD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 230 ])

c8quBHD2x1Re = Parameter(name = 'c8quBHD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quBHD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 231 ])

c8quBHD2x1Im = Parameter(name = 'c8quBHD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quBHD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 232 ])

c8quBHD2x2Re = Parameter(name = 'c8quBHD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quBHD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 233 ])

c8quBHD2x2Im = Parameter(name = 'c8quBHD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quBHD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 234 ])

c8quBHD2x3Re = Parameter(name = 'c8quBHD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quBHD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 235 ])

c8quBHD2x3Im = Parameter(name = 'c8quBHD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quBHD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 236 ])

c8qdGHD2x1Re = Parameter(name = 'c8qdGHD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdGHD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 237 ])

c8qdGHD2x1Im = Parameter(name = 'c8qdGHD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdGHD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 238 ])

c8qdGHD2x2Re = Parameter(name = 'c8qdGHD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdGHD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 239 ])

c8qdGHD2x2Im = Parameter(name = 'c8qdGHD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdGHD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 240 ])

c8qdGHD2x3Re = Parameter(name = 'c8qdGHD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdGHD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 241 ])

c8qdGHD2x3Im = Parameter(name = 'c8qdGHD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdGHD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 242 ])

c8qdWHD2x1Re = Parameter(name = 'c8qdWHD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdWHD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 243 ])

c8qdWHD2x1Im = Parameter(name = 'c8qdWHD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdWHD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 244 ])

c8qdWHD2x2Re = Parameter(name = 'c8qdWHD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdWHD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 245 ])

c8qdWHD2x2Im = Parameter(name = 'c8qdWHD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdWHD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 246 ])

c8qdWHD2x3Re = Parameter(name = 'c8qdWHD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdWHD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 247 ])

c8qdWHD2x3Im = Parameter(name = 'c8qdWHD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdWHD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 248 ])

c8qdBHD2x1Re = Parameter(name = 'c8qdBHD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdBHD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 249 ])

c8qdBHD2x1Im = Parameter(name = 'c8qdBHD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdBHD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 250 ])

c8qdBHD2x2Re = Parameter(name = 'c8qdBHD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdBHD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 251 ])

c8qdBHD2x2Im = Parameter(name = 'c8qdBHD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdBHD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 252 ])

c8qdBHD2x3Re = Parameter(name = 'c8qdBHD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdBHD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 253 ])

c8qdBHD2x3Im = Parameter(name = 'c8qdBHD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdBHD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 254 ])

c8leH3D2x1Re = Parameter(name = 'c8leH3D2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 255 ])

c8leH3D2x1Im = Parameter(name = 'c8leH3D2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 256 ])

c8leH3D2x2Re = Parameter(name = 'c8leH3D2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 257 ])

c8leH3D2x2Im = Parameter(name = 'c8leH3D2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 258 ])

c8leH3D2x3Re = Parameter(name = 'c8leH3D2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 259 ])

c8leH3D2x3Im = Parameter(name = 'c8leH3D2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 260 ])

c8leH3D2x4Re = Parameter(name = 'c8leH3D2x4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 261 ])

c8leH3D2x4Im = Parameter(name = 'c8leH3D2x4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 262 ])

c8leH3D2x5Re = Parameter(name = 'c8leH3D2x5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 263 ])

c8leH3D2x5Im = Parameter(name = 'c8leH3D2x5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 264 ])

c8leH3D2x6Re = Parameter(name = 'c8leH3D2x6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 265 ])

c8leH3D2x6Im = Parameter(name = 'c8leH3D2x6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leH3D2x6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 266 ])

c8quH3D2x1Re = Parameter(name = 'c8quH3D2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 267 ])

c8quH3D2x1Im = Parameter(name = 'c8quH3D2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 268 ])

c8quH3D2x2Re = Parameter(name = 'c8quH3D2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 269 ])

c8quH3D2x2Im = Parameter(name = 'c8quH3D2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 270 ])

c8quH3D2x3Re = Parameter(name = 'c8quH3D2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 271 ])

c8quH3D2x3Im = Parameter(name = 'c8quH3D2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 272 ])

c8quH3D2x4Re = Parameter(name = 'c8quH3D2x4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 273 ])

c8quH3D2x4Im = Parameter(name = 'c8quH3D2x4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 274 ])

c8quH3D2x5Re = Parameter(name = 'c8quH3D2x5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 275 ])

c8quH3D2x5Im = Parameter(name = 'c8quH3D2x5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 276 ])

c8quH3D2x6Re = Parameter(name = 'c8quH3D2x6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 277 ])

c8quH3D2x6Im = Parameter(name = 'c8quH3D2x6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8quH3D2x6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 278 ])

c8qdH3D2x1Re = Parameter(name = 'c8qdH3D2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 279 ])

c8qdH3D2x1Im = Parameter(name = 'c8qdH3D2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 280 ])

c8qdH3D2x2Re = Parameter(name = 'c8qdH3D2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 281 ])

c8qdH3D2x2Im = Parameter(name = 'c8qdH3D2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 282 ])

c8qdH3D2x3Re = Parameter(name = 'c8qdH3D2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 283 ])

c8qdH3D2x3Im = Parameter(name = 'c8qdH3D2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 284 ])

c8qdH3D2x4Re = Parameter(name = 'c8qdH3D2x4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 285 ])

c8qdH3D2x4Im = Parameter(name = 'c8qdH3D2x4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 286 ])

c8qdH3D2x5Re = Parameter(name = 'c8qdH3D2x5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 287 ])

c8qdH3D2x5Im = Parameter(name = 'c8qdH3D2x5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 288 ])

c8qdH3D2x6Re = Parameter(name = 'c8qdH3D2x6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 289 ])

c8qdH3D2x6Im = Parameter(name = 'c8qdH3D2x6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qdH3D2x6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 290 ])

c8leqdH2x1Re = Parameter(name = 'c8leqdH2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdH2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 291 ])

c8leqdH2x1Im = Parameter(name = 'c8leqdH2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdH2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 292 ])

c8leqdH2x2Re = Parameter(name = 'c8leqdH2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdH2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 293 ])

c8leqdH2x2Im = Parameter(name = 'c8leqdH2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdH2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 294 ])

c8l2udH2Re = Parameter(name = 'c8l2udH2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8l2udH2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 295 ])

c8l2udH2Im = Parameter(name = 'c8l2udH2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8l2udH2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 296 ])

c8lequH2x5Re = Parameter(name = 'c8lequH2x5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 297 ])

c8lequH2x5Im = Parameter(name = 'c8lequH2x5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 298 ])

c8q2udH2x5Re = Parameter(name = 'c8q2udH2x5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 299 ])

c8q2udH2x5Im = Parameter(name = 'c8q2udH2x5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 300 ])

c8q2udH2x6Re = Parameter(name = 'c8q2udH2x6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 301 ])

c8q2udH2x6Im = Parameter(name = 'c8q2udH2x6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 302 ])

c8leqdD2x1Re = Parameter(name = 'c8leqdD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 303 ])

c8leqdD2x1Im = Parameter(name = 'c8leqdD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 304 ])

c8leqdD2x2Re = Parameter(name = 'c8leqdD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 305 ])

c8leqdD2x2Im = Parameter(name = 'c8leqdD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 306 ])

c8l4H2x1 = Parameter(name = 'c8l4H2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{l4H2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 307 ])

c8l4H2x2 = Parameter(name = 'c8l4H2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{l4H2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 308 ])

c8q4H2x1 = Parameter(name = 'c8q4H2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{q4H2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 309 ])

c8q4H2x2 = Parameter(name = 'c8q4H2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{q4H2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 310 ])

c8q4H2x3 = Parameter(name = 'c8q4H2x3',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{q4H2x3}}',
                     lhablock = 'DIM8',
                     lhacode = [ 311 ])

c8l2q2H2x1 = Parameter(name = 'c8l2q2H2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2H2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 312 ])

c8l2q2H2x2 = Parameter(name = 'c8l2q2H2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2H2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 313 ])

c8l2q2H2x3 = Parameter(name = 'c8l2q2H2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2H2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 314 ])

c8l2q2H2x4 = Parameter(name = 'c8l2q2H2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2H2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 315 ])

c8l2q2H2x5 = Parameter(name = 'c8l2q2H2x5',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2H2x5}}',
                       lhablock = 'DIM8',
                       lhacode = [ 316 ])

c8q4H2x5 = Parameter(name = 'c8q4H2x5',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{q4H2x5}}',
                     lhablock = 'DIM8',
                     lhacode = [ 317 ])

c8e4H2 = Parameter(name = 'c8e4H2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{e4H2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 318 ])

c8u4H2 = Parameter(name = 'c8u4H2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{u4H2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 319 ])

c8d4H2 = Parameter(name = 'c8d4H2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{d4H2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 320 ])

c8e2u2H2 = Parameter(name = 'c8e2u2H2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{e2u2H2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 321 ])

c8e2d2H2 = Parameter(name = 'c8e2d2H2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{e2d2H2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 322 ])

c8u2d2H2x1 = Parameter(name = 'c8u2d2H2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2d2H2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 323 ])

c8u2d2H2x2 = Parameter(name = 'c8u2d2H2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2d2H2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 324 ])

c8l2e2H2x1 = Parameter(name = 'c8l2e2H2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2e2H2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 325 ])

c8l2e2H2x2 = Parameter(name = 'c8l2e2H2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2e2H2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 326 ])

c8l2u2H2x1 = Parameter(name = 'c8l2u2H2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2u2H2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 327 ])

c8l2u2H2x2 = Parameter(name = 'c8l2u2H2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2u2H2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 328 ])

c8l2d2H2x1 = Parameter(name = 'c8l2d2H2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2d2H2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 329 ])

c8l2d2H2x2 = Parameter(name = 'c8l2d2H2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2d2H2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 330 ])

c8q2e2H2x1 = Parameter(name = 'c8q2e2H2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2e2H2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 331 ])

c8q2e2H2x2 = Parameter(name = 'c8q2e2H2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2e2H2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 332 ])

c8q2u2H2x1 = Parameter(name = 'c8q2u2H2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2u2H2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 333 ])

c8q2u2H2x2 = Parameter(name = 'c8q2u2H2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2u2H2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 334 ])

c8q2u2H2x3 = Parameter(name = 'c8q2u2H2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2u2H2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 335 ])

c8q2u2H2x4 = Parameter(name = 'c8q2u2H2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2u2H2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 336 ])

c8q2d2H2x1 = Parameter(name = 'c8q2d2H2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2d2H2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 337 ])

c8q2d2H2x2 = Parameter(name = 'c8q2d2H2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2d2H2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 338 ])

c8q2d2H2x3 = Parameter(name = 'c8q2d2H2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2d2H2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 339 ])

c8q2d2H2x4 = Parameter(name = 'c8q2d2H2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2d2H2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 340 ])

c8q2udH2x1Re = Parameter(name = 'c8q2udH2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 341 ])

c8q2udH2x1Im = Parameter(name = 'c8q2udH2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 342 ])

c8q2udH2x2Re = Parameter(name = 'c8q2udH2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 343 ])

c8q2udH2x2Im = Parameter(name = 'c8q2udH2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 344 ])

c8q2udH2x3Re = Parameter(name = 'c8q2udH2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 345 ])

c8q2udH2x3Im = Parameter(name = 'c8q2udH2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 346 ])

c8q2udH2x4Re = Parameter(name = 'c8q2udH2x4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 347 ])

c8q2udH2x4Im = Parameter(name = 'c8q2udH2x4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udH2x4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 348 ])

c8lequH2x1Re = Parameter(name = 'c8lequH2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 349 ])

c8lequH2x1Im = Parameter(name = 'c8lequH2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 350 ])

c8lequH2x2Re = Parameter(name = 'c8lequH2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 351 ])

c8lequH2x2Im = Parameter(name = 'c8lequH2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 352 ])

c8lequH2x3Re = Parameter(name = 'c8lequH2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 353 ])

c8lequH2x3Im = Parameter(name = 'c8lequH2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 354 ])

c8lequH2x4Re = Parameter(name = 'c8lequH2x4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 355 ])

c8lequH2x4Im = Parameter(name = 'c8lequH2x4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequH2x4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 356 ])

c8l2e2H2x3Re = Parameter(name = 'c8l2e2H2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2e2H2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 357 ])

c8l2e2H2x3Im = Parameter(name = 'c8l2e2H2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2e2H2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 358 ])

c8leqdH2x3Re = Parameter(name = 'c8leqdH2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdH2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 359 ])

c8leqdH2x3Im = Parameter(name = 'c8leqdH2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdH2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 360 ])

c8leqdH2x4Re = Parameter(name = 'c8leqdH2x4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdH2x4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 361 ])

c8leqdH2x4Im = Parameter(name = 'c8leqdH2x4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leqdH2x4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 362 ])

c8q2u2H2x5Re = Parameter(name = 'c8q2u2H2x5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2u2H2x5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 363 ])

c8q2u2H2x5Im = Parameter(name = 'c8q2u2H2x5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2u2H2x5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 364 ])

c8q2u2H2x6Re = Parameter(name = 'c8q2u2H2x6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2u2H2x6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 365 ])

c8q2u2H2x6Im = Parameter(name = 'c8q2u2H2x6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2u2H2x6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 366 ])

c8q2d2H2x5Re = Parameter(name = 'c8q2d2H2x5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2d2H2x5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 367 ])

c8q2d2H2x5Im = Parameter(name = 'c8q2d2H2x5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2d2H2x5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 368 ])

c8q2d2H2x6Re = Parameter(name = 'c8q2d2H2x6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2d2H2x6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 369 ])

c8q2d2H2x6Im = Parameter(name = 'c8q2d2H2x6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2d2H2x6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 370 ])

c8l4Wx1 = Parameter(name = 'c8l4Wx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{l4Wx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 371 ])

c8l4Wx2 = Parameter(name = 'c8l4Wx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{l4Wx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 372 ])

c8q4Gx1 = Parameter(name = 'c8q4Gx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Gx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 373 ])

c8q4Gx2 = Parameter(name = 'c8q4Gx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Gx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 374 ])

c8q4Gx3 = Parameter(name = 'c8q4Gx3',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Gx3}}',
                    lhablock = 'DIM8',
                    lhacode = [ 375 ])

c8q4Gx4 = Parameter(name = 'c8q4Gx4',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Gx4}}',
                    lhablock = 'DIM8',
                    lhacode = [ 376 ])

c8q4Wx1 = Parameter(name = 'c8q4Wx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Wx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 377 ])

c8q4Wx2 = Parameter(name = 'c8q4Wx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Wx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 378 ])

c8q4Wx3 = Parameter(name = 'c8q4Wx3',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Wx3}}',
                    lhablock = 'DIM8',
                    lhacode = [ 379 ])

c8q4Wx4 = Parameter(name = 'c8q4Wx4',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Wx4}}',
                    lhablock = 'DIM8',
                    lhacode = [ 380 ])

c8l2q2Gx1 = Parameter(name = 'c8l2q2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 381 ])

c8l2q2Gx2 = Parameter(name = 'c8l2q2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 382 ])

c8l2q2Gx3 = Parameter(name = 'c8l2q2Gx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Gx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 383 ])

c8l2q2Gx4 = Parameter(name = 'c8l2q2Gx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Gx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 384 ])

c8l2q2Wx1 = Parameter(name = 'c8l2q2Wx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Wx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 385 ])

c8l2q2Wx2 = Parameter(name = 'c8l2q2Wx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Wx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 386 ])

c8l2q2Wx3 = Parameter(name = 'c8l2q2Wx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Wx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 387 ])

c8l2q2Wx4 = Parameter(name = 'c8l2q2Wx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Wx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 388 ])

c8l2q2Wx5 = Parameter(name = 'c8l2q2Wx5',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Wx5}}',
                      lhablock = 'DIM8',
                      lhacode = [ 389 ])

c8l2q2Wx6 = Parameter(name = 'c8l2q2Wx6',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Wx6}}',
                      lhablock = 'DIM8',
                      lhacode = [ 390 ])

c8l2q2Bx1 = Parameter(name = 'c8l2q2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 391 ])

c8l2q2Bx2 = Parameter(name = 'c8l2q2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 392 ])

c8l2q2Bx3 = Parameter(name = 'c8l2q2Bx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Bx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 393 ])

c8l2q2Bx4 = Parameter(name = 'c8l2q2Bx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2q2Bx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 394 ])

c8l4Bx1 = Parameter(name = 'c8l4Bx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{l4Bx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 395 ])

c8l4Bx2 = Parameter(name = 'c8l4Bx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{l4Bx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 396 ])

c8q4Bx1 = Parameter(name = 'c8q4Bx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Bx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 397 ])

c8q4Bx2 = Parameter(name = 'c8q4Bx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Bx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 398 ])

c8q4Bx3 = Parameter(name = 'c8q4Bx3',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Bx3}}',
                    lhablock = 'DIM8',
                    lhacode = [ 399 ])

c8q4Bx4 = Parameter(name = 'c8q4Bx4',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{q4Bx4}}',
                    lhablock = 'DIM8',
                    lhacode = [ 400 ])

c8u4Gx1 = Parameter(name = 'c8u4Gx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{u4Gx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 401 ])

c8u4Gx2 = Parameter(name = 'c8u4Gx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{u4Gx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 402 ])

c8d4Gx1 = Parameter(name = 'c8d4Gx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{d4Gx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 403 ])

c8d4Gx2 = Parameter(name = 'c8d4Gx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{d4Gx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 404 ])

c8e2u2Gx1 = Parameter(name = 'c8e2u2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{e2u2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 405 ])

c8e2u2Gx2 = Parameter(name = 'c8e2u2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{e2u2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 406 ])

c8e2u2Bx1 = Parameter(name = 'c8e2u2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{e2u2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 407 ])

c8e2u2Bx2 = Parameter(name = 'c8e2u2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{e2u2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 408 ])

c8e2d2Gx1 = Parameter(name = 'c8e2d2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{e2d2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 409 ])

c8e2d2Gx2 = Parameter(name = 'c8e2d2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{e2d2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 410 ])

c8e2d2Bx1 = Parameter(name = 'c8e2d2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{e2d2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 411 ])

c8e2d2Bx2 = Parameter(name = 'c8e2d2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{e2d2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 412 ])

c8u2d2Gx1 = Parameter(name = 'c8u2d2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 413 ])

c8u2d2Gx2 = Parameter(name = 'c8u2d2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 414 ])

c8u2d2Gx3 = Parameter(name = 'c8u2d2Gx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Gx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 415 ])

c8u2d2Gx4 = Parameter(name = 'c8u2d2Gx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Gx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 416 ])

c8u2d2Gx5 = Parameter(name = 'c8u2d2Gx5',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Gx5}}',
                      lhablock = 'DIM8',
                      lhacode = [ 417 ])

c8u2d2Gx6 = Parameter(name = 'c8u2d2Gx6',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Gx6}}',
                      lhablock = 'DIM8',
                      lhacode = [ 418 ])

c8u2d2Gx7 = Parameter(name = 'c8u2d2Gx7',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Gx7}}',
                      lhablock = 'DIM8',
                      lhacode = [ 419 ])

c8u2d2Gx8 = Parameter(name = 'c8u2d2Gx8',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Gx8}}',
                      lhablock = 'DIM8',
                      lhacode = [ 420 ])

c8u2d2Bx1 = Parameter(name = 'c8u2d2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 421 ])

c8u2d2Bx2 = Parameter(name = 'c8u2d2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 422 ])

c8u2d2Bx3 = Parameter(name = 'c8u2d2Bx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Bx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 423 ])

c8u2d2Bx4 = Parameter(name = 'c8u2d2Bx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{u2d2Bx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 424 ])

c8e4Bx1 = Parameter(name = 'c8e4Bx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{e4Bx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 425 ])

c8e4Bx2 = Parameter(name = 'c8e4Bx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{e4Bx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 426 ])

c8u4Bx1 = Parameter(name = 'c8u4Bx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{u4Bx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 427 ])

c8u4Bx2 = Parameter(name = 'c8u4Bx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{u4Bx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 428 ])

c8d4Bx1 = Parameter(name = 'c8d4Bx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{d4Bx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 429 ])

c8d4Bx2 = Parameter(name = 'c8d4Bx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{d4Bx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 430 ])

c8l2e2Wx1 = Parameter(name = 'c8l2e2Wx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2e2Wx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 431 ])

c8l2e2Wx2 = Parameter(name = 'c8l2e2Wx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2e2Wx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 432 ])

c8l2e2Bx1 = Parameter(name = 'c8l2e2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2e2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 433 ])

c8l2e2Bx2 = Parameter(name = 'c8l2e2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2e2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 434 ])

c8l2u2Gx1 = Parameter(name = 'c8l2u2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2u2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 435 ])

c8l2u2Gx2 = Parameter(name = 'c8l2u2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2u2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 436 ])

c8l2u2Wx1 = Parameter(name = 'c8l2u2Wx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2u2Wx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 437 ])

c8l2u2Wx2 = Parameter(name = 'c8l2u2Wx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2u2Wx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 438 ])

c8l2u2Bx1 = Parameter(name = 'c8l2u2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2u2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 439 ])

c8l2u2Bx2 = Parameter(name = 'c8l2u2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2u2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 440 ])

c8l2d2Gx1 = Parameter(name = 'c8l2d2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2d2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 441 ])

c8l2d2Gx2 = Parameter(name = 'c8l2d2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2d2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 442 ])

c8l2d2Wx1 = Parameter(name = 'c8l2d2Wx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2d2Wx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 443 ])

c8l2d2Wx2 = Parameter(name = 'c8l2d2Wx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2d2Wx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 444 ])

c8l2d2Bx1 = Parameter(name = 'c8l2d2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2d2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 445 ])

c8l2d2Bx2 = Parameter(name = 'c8l2d2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{l2d2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 446 ])

c8q2e2Gx1 = Parameter(name = 'c8q2e2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2e2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 447 ])

c8q2e2Gx2 = Parameter(name = 'c8q2e2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2e2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 448 ])

c8q2e2Wx1 = Parameter(name = 'c8q2e2Wx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2e2Wx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 449 ])

c8q2e2Wx2 = Parameter(name = 'c8q2e2Wx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2e2Wx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 450 ])

c8q2e2Bx1 = Parameter(name = 'c8q2e2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2e2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 451 ])

c8q2e2Bx2 = Parameter(name = 'c8q2e2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2e2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 452 ])

c8q2u2Gx1 = Parameter(name = 'c8q2u2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 453 ])

c8q2u2Gx2 = Parameter(name = 'c8q2u2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 454 ])

c8q2u2Gx3 = Parameter(name = 'c8q2u2Gx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Gx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 455 ])

c8q2u2Gx4 = Parameter(name = 'c8q2u2Gx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Gx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 456 ])

c8q2u2Gx5 = Parameter(name = 'c8q2u2Gx5',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Gx5}}',
                      lhablock = 'DIM8',
                      lhacode = [ 457 ])

c8q2u2Gx6 = Parameter(name = 'c8q2u2Gx6',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Gx6}}',
                      lhablock = 'DIM8',
                      lhacode = [ 458 ])

c8q2u2Gx7 = Parameter(name = 'c8q2u2Gx7',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Gx7}}',
                      lhablock = 'DIM8',
                      lhacode = [ 459 ])

c8q2u2Gx8 = Parameter(name = 'c8q2u2Gx8',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Gx8}}',
                      lhablock = 'DIM8',
                      lhacode = [ 460 ])

c8q2u2Wx1 = Parameter(name = 'c8q2u2Wx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Wx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 461 ])

c8q2u2Wx2 = Parameter(name = 'c8q2u2Wx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Wx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 462 ])

c8q2u2Wx3 = Parameter(name = 'c8q2u2Wx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Wx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 463 ])

c8q2u2Wx4 = Parameter(name = 'c8q2u2Wx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Wx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 464 ])

c8q2u2Bx1 = Parameter(name = 'c8q2u2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 465 ])

c8q2u2Bx2 = Parameter(name = 'c8q2u2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 466 ])

c8q2u2Bx3 = Parameter(name = 'c8q2u2Bx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Bx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 467 ])

c8q2u2Bx4 = Parameter(name = 'c8q2u2Bx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2u2Bx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 468 ])

c8q2d2Gx1 = Parameter(name = 'c8q2d2Gx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Gx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 469 ])

c8q2d2Gx2 = Parameter(name = 'c8q2d2Gx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Gx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 470 ])

c8q2d2Gx3 = Parameter(name = 'c8q2d2Gx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Gx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 471 ])

c8q2d2Gx4 = Parameter(name = 'c8q2d2Gx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Gx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 472 ])

c8q2d2Gx5 = Parameter(name = 'c8q2d2Gx5',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Gx5}}',
                      lhablock = 'DIM8',
                      lhacode = [ 473 ])

c8q2d2Gx6 = Parameter(name = 'c8q2d2Gx6',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Gx6}}',
                      lhablock = 'DIM8',
                      lhacode = [ 474 ])

c8q2d2Gx7 = Parameter(name = 'c8q2d2Gx7',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Gx7}}',
                      lhablock = 'DIM8',
                      lhacode = [ 475 ])

c8q2d2Gx8 = Parameter(name = 'c8q2d2Gx8',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Gx8}}',
                      lhablock = 'DIM8',
                      lhacode = [ 476 ])

c8q2d2Wx1 = Parameter(name = 'c8q2d2Wx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Wx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 477 ])

c8q2d2Wx2 = Parameter(name = 'c8q2d2Wx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Wx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 478 ])

c8q2d2Wx3 = Parameter(name = 'c8q2d2Wx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Wx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 479 ])

c8q2d2Wx4 = Parameter(name = 'c8q2d2Wx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Wx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 480 ])

c8q2d2Bx1 = Parameter(name = 'c8q2d2Bx1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Bx1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 481 ])

c8q2d2Bx2 = Parameter(name = 'c8q2d2Bx2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Bx2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 482 ])

c8q2d2Bx3 = Parameter(name = 'c8q2d2Bx3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Bx3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 483 ])

c8q2d2Bx4 = Parameter(name = 'c8q2d2Bx4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{q2d2Bx4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 484 ])

c8ledqGx1Re = Parameter(name = 'c8ledqGx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqGx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 485 ])

c8ledqGx1Im = Parameter(name = 'c8ledqGx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqGx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 486 ])

c8ledqGx2Re = Parameter(name = 'c8ledqGx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqGx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 487 ])

c8ledqGx2Im = Parameter(name = 'c8ledqGx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqGx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 488 ])

c8ledqWx1Re = Parameter(name = 'c8ledqWx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqWx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 489 ])

c8ledqWx1Im = Parameter(name = 'c8ledqWx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqWx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 490 ])

c8ledqWx2Re = Parameter(name = 'c8ledqWx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqWx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 491 ])

c8ledqWx2Im = Parameter(name = 'c8ledqWx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqWx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 492 ])

c8ledqBx1Re = Parameter(name = 'c8ledqBx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqBx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 493 ])

c8ledqBx1Im = Parameter(name = 'c8ledqBx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqBx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 494 ])

c8ledqBx2Re = Parameter(name = 'c8ledqBx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqBx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 495 ])

c8ledqBx2Im = Parameter(name = 'c8ledqBx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8ledqBx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 496 ])

c8q2udGx1Re = Parameter(name = 'c8q2udGx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 497 ])

c8q2udGx1Im = Parameter(name = 'c8q2udGx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 498 ])

c8q2udGx2Re = Parameter(name = 'c8q2udGx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 499 ])

c8q2udGx2Im = Parameter(name = 'c8q2udGx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 500 ])

c8q2udGx3Re = Parameter(name = 'c8q2udGx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 501 ])

c8q2udGx3Im = Parameter(name = 'c8q2udGx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 502 ])

c8q2udGx4Re = Parameter(name = 'c8q2udGx4Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx4Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 503 ])

c8q2udGx4Im = Parameter(name = 'c8q2udGx4Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx4Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 504 ])

c8q2udGx5Re = Parameter(name = 'c8q2udGx5Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx5Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 505 ])

c8q2udGx5Im = Parameter(name = 'c8q2udGx5Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx5Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 506 ])

c8q2udGx6Re = Parameter(name = 'c8q2udGx6Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx6Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 507 ])

c8q2udGx6Im = Parameter(name = 'c8q2udGx6Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udGx6Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 508 ])

c8q2udWx1Re = Parameter(name = 'c8q2udWx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udWx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 509 ])

c8q2udWx1Im = Parameter(name = 'c8q2udWx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udWx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 510 ])

c8q2udWx2Re = Parameter(name = 'c8q2udWx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udWx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 511 ])

c8q2udWx2Im = Parameter(name = 'c8q2udWx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udWx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 512 ])

c8q2udWx3Re = Parameter(name = 'c8q2udWx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udWx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 513 ])

c8q2udWx3Im = Parameter(name = 'c8q2udWx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udWx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 514 ])

c8q2udBx1Re = Parameter(name = 'c8q2udBx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udBx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 515 ])

c8q2udBx1Im = Parameter(name = 'c8q2udBx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udBx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 516 ])

c8q2udBx2Re = Parameter(name = 'c8q2udBx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udBx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 517 ])

c8q2udBx2Im = Parameter(name = 'c8q2udBx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udBx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 518 ])

c8q2udBx3Re = Parameter(name = 'c8q2udBx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udBx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 519 ])

c8q2udBx3Im = Parameter(name = 'c8q2udBx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q2udBx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 520 ])

c8lequGx1Re = Parameter(name = 'c8lequGx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequGx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 521 ])

c8lequGx1Im = Parameter(name = 'c8lequGx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequGx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 522 ])

c8lequGx2Re = Parameter(name = 'c8lequGx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequGx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 523 ])

c8lequGx2Im = Parameter(name = 'c8lequGx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequGx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 524 ])

c8lequGx3Re = Parameter(name = 'c8lequGx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequGx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 525 ])

c8lequGx3Im = Parameter(name = 'c8lequGx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequGx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 526 ])

c8lequWx1Re = Parameter(name = 'c8lequWx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequWx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 527 ])

c8lequWx1Im = Parameter(name = 'c8lequWx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequWx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 528 ])

c8lequWx2Re = Parameter(name = 'c8lequWx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequWx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 529 ])

c8lequWx2Im = Parameter(name = 'c8lequWx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequWx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 530 ])

c8lequWx3Re = Parameter(name = 'c8lequWx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequWx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 531 ])

c8lequWx3Im = Parameter(name = 'c8lequWx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequWx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 532 ])

c8lequBx1Re = Parameter(name = 'c8lequBx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequBx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 533 ])

c8lequBx1Im = Parameter(name = 'c8lequBx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequBx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 534 ])

c8lequBx2Re = Parameter(name = 'c8lequBx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequBx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 535 ])

c8lequBx2Im = Parameter(name = 'c8lequBx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequBx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 536 ])

c8lequBx3Re = Parameter(name = 'c8lequBx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequBx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 537 ])

c8lequBx3Im = Parameter(name = 'c8lequBx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lequBx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 538 ])

c8G4x1 = Parameter(name = 'c8G4x1',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x1}}',
                   lhablock = 'DIM8',
                   lhacode = [ 539 ])

c8G4x2 = Parameter(name = 'c8G4x2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 540 ])

c8G4x3 = Parameter(name = 'c8G4x3',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x3}}',
                   lhablock = 'DIM8',
                   lhacode = [ 541 ])

c8G4x4 = Parameter(name = 'c8G4x4',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x4}}',
                   lhablock = 'DIM8',
                   lhacode = [ 542 ])

c8G4x5 = Parameter(name = 'c8G4x5',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x5}}',
                   lhablock = 'DIM8',
                   lhacode = [ 543 ])

c8G4x6 = Parameter(name = 'c8G4x6',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x6}}',
                   lhablock = 'DIM8',
                   lhacode = [ 544 ])

c8G4x7 = Parameter(name = 'c8G4x7',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x7}}',
                   lhablock = 'DIM8',
                   lhacode = [ 545 ])

c8G4x8 = Parameter(name = 'c8G4x8',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x8}}',
                   lhablock = 'DIM8',
                   lhacode = [ 546 ])

c8G4x9 = Parameter(name = 'c8G4x9',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{G4x9}}',
                   lhablock = 'DIM8',
                   lhacode = [ 547 ])

c8W4x1 = Parameter(name = 'c8W4x1',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{W4x1}}',
                   lhablock = 'DIM8',
                   lhacode = [ 548 ])

c8W4x2 = Parameter(name = 'c8W4x2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{W4x2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 549 ])

c8W4x3 = Parameter(name = 'c8W4x3',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{W4x3}}',
                   lhablock = 'DIM8',
                   lhacode = [ 550 ])

c8W4x4 = Parameter(name = 'c8W4x4',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{W4x4}}',
                   lhablock = 'DIM8',
                   lhacode = [ 551 ])

c8W4x5 = Parameter(name = 'c8W4x5',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{W4x5}}',
                   lhablock = 'DIM8',
                   lhacode = [ 552 ])

c8W4x6 = Parameter(name = 'c8W4x6',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{W4x6}}',
                   lhablock = 'DIM8',
                   lhacode = [ 553 ])

c8B4x1 = Parameter(name = 'c8B4x1',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{B4x1}}',
                   lhablock = 'DIM8',
                   lhacode = [ 554 ])

c8B4x2 = Parameter(name = 'c8B4x2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{B4x2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 555 ])

c8B4x3 = Parameter(name = 'c8B4x3',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{B4x3}}',
                   lhablock = 'DIM8',
                   lhacode = [ 556 ])

c8G3Bx1 = Parameter(name = 'c8G3Bx1',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{G3Bx1}}',
                    lhablock = 'DIM8',
                    lhacode = [ 557 ])

c8G3Bx2 = Parameter(name = 'c8G3Bx2',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{G3Bx2}}',
                    lhablock = 'DIM8',
                    lhacode = [ 558 ])

c8G3Bx3 = Parameter(name = 'c8G3Bx3',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{G3Bx3}}',
                    lhablock = 'DIM8',
                    lhacode = [ 559 ])

c8G3Bx4 = Parameter(name = 'c8G3Bx4',
                    nature = 'external',
                    type = 'real',
                    value = 0,
                    texname = 'c_{8 \\text{G3Bx4}}',
                    lhablock = 'DIM8',
                    lhacode = [ 560 ])

c8G2W2x1 = Parameter(name = 'c8G2W2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2W2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 561 ])

c8G2W2x2 = Parameter(name = 'c8G2W2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2W2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 562 ])

c8G2W2x3 = Parameter(name = 'c8G2W2x3',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2W2x3}}',
                     lhablock = 'DIM8',
                     lhacode = [ 563 ])

c8G2W2x4 = Parameter(name = 'c8G2W2x4',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2W2x4}}',
                     lhablock = 'DIM8',
                     lhacode = [ 564 ])

c8G2W2x5 = Parameter(name = 'c8G2W2x5',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2W2x5}}',
                     lhablock = 'DIM8',
                     lhacode = [ 565 ])

c8G2W2x6 = Parameter(name = 'c8G2W2x6',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2W2x6}}',
                     lhablock = 'DIM8',
                     lhacode = [ 566 ])

c8G2W2x7 = Parameter(name = 'c8G2W2x7',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2W2x7}}',
                     lhablock = 'DIM8',
                     lhacode = [ 567 ])

c8G2B2x1 = Parameter(name = 'c8G2B2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2B2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 568 ])

c8G2B2x2 = Parameter(name = 'c8G2B2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2B2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 569 ])

c8G2B2x3 = Parameter(name = 'c8G2B2x3',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2B2x3}}',
                     lhablock = 'DIM8',
                     lhacode = [ 570 ])

c8G2B2x4 = Parameter(name = 'c8G2B2x4',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2B2x4}}',
                     lhablock = 'DIM8',
                     lhacode = [ 571 ])

c8G2B2x5 = Parameter(name = 'c8G2B2x5',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2B2x5}}',
                     lhablock = 'DIM8',
                     lhacode = [ 572 ])

c8G2B2x6 = Parameter(name = 'c8G2B2x6',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2B2x6}}',
                     lhablock = 'DIM8',
                     lhacode = [ 573 ])

c8G2B2x7 = Parameter(name = 'c8G2B2x7',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2B2x7}}',
                     lhablock = 'DIM8',
                     lhacode = [ 574 ])

c8W2B2x1 = Parameter(name = 'c8W2B2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2B2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 575 ])

c8W2B2x2 = Parameter(name = 'c8W2B2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2B2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 576 ])

c8W2B2x3 = Parameter(name = 'c8W2B2x3',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2B2x3}}',
                     lhablock = 'DIM8',
                     lhacode = [ 577 ])

c8W2B2x4 = Parameter(name = 'c8W2B2x4',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2B2x4}}',
                     lhablock = 'DIM8',
                     lhacode = [ 578 ])

c8W2B2x5 = Parameter(name = 'c8W2B2x5',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2B2x5}}',
                     lhablock = 'DIM8',
                     lhacode = [ 579 ])

c8W2B2x6 = Parameter(name = 'c8W2B2x6',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2B2x6}}',
                     lhablock = 'DIM8',
                     lhacode = [ 580 ])

c8W2B2x7 = Parameter(name = 'c8W2B2x7',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2B2x7}}',
                     lhablock = 'DIM8',
                     lhacode = [ 581 ])

c8H8 = Parameter(name = 'c8H8',
                 nature = 'external',
                 type = 'real',
                 value = 0,
                 texname = 'c_{8 \\text{H8}}',
                 lhablock = 'DIM8',
                 lhacode = [ 582 ])

c8H6x1 = Parameter(name = 'c8H6x1',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{H6x1}}',
                   lhablock = 'DIM8',
                   lhacode = [ 583 ])

c8H6x2 = Parameter(name = 'c8H6x2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{H6x2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 584 ])

c8H4x1 = Parameter(name = 'c8H4x1',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{H4x1}}',
                   lhablock = 'DIM8',
                   lhacode = [ 585 ])

c8H4x2 = Parameter(name = 'c8H4x2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{H4x2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 586 ])

c8H4x3 = Parameter(name = 'c8H4x3',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{H4x3}}',
                   lhablock = 'DIM8',
                   lhacode = [ 587 ])

c8l3eHDx1Re = Parameter(name = 'c8l3eHDx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8l3eHDx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 588 ])

c8l3eHDx1Im = Parameter(name = 'c8l3eHDx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8l3eHDx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 589 ])

c8l3eHDx2Re = Parameter(name = 'c8l3eHDx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8l3eHDx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 590 ])

c8l3eHDx2Im = Parameter(name = 'c8l3eHDx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8l3eHDx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 591 ])

c8l3eHDx3Re = Parameter(name = 'c8l3eHDx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8l3eHDx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 592 ])

c8l3eHDx3Im = Parameter(name = 'c8l3eHDx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8l3eHDx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 593 ])

c8le3HDx1Re = Parameter(name = 'c8le3HDx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8le3HDx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 594 ])

c8le3HDx1Im = Parameter(name = 'c8le3HDx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8le3HDx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 595 ])

c8leq2HDx1Re = Parameter(name = 'c8leq2HDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 596 ])

c8leq2HDx1Im = Parameter(name = 'c8leq2HDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 597 ])

c8leq2HDx2Re = Parameter(name = 'c8leq2HDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 598 ])

c8leq2HDx2Im = Parameter(name = 'c8leq2HDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 599 ])

c8leq2HDx3Re = Parameter(name = 'c8leq2HDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 600 ])

c8leq2HDx3Im = Parameter(name = 'c8leq2HDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 601 ])

c8leq2HDx4Re = Parameter(name = 'c8leq2HDx4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 602 ])

c8leq2HDx4Im = Parameter(name = 'c8leq2HDx4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 603 ])

c8leq2HDx5Re = Parameter(name = 'c8leq2HDx5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 604 ])

c8leq2HDx5Im = Parameter(name = 'c8leq2HDx5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 605 ])

c8leq2HDx6Re = Parameter(name = 'c8leq2HDx6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 606 ])

c8leq2HDx6Im = Parameter(name = 'c8leq2HDx6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leq2HDx6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 607 ])

c8leu2HDx1Re = Parameter(name = 'c8leu2HDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leu2HDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 608 ])

c8leu2HDx1Im = Parameter(name = 'c8leu2HDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leu2HDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 609 ])

c8leu2HDx2Re = Parameter(name = 'c8leu2HDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leu2HDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 610 ])

c8leu2HDx2Im = Parameter(name = 'c8leu2HDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leu2HDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 611 ])

c8leu2HDx3Re = Parameter(name = 'c8leu2HDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leu2HDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 612 ])

c8leu2HDx3Im = Parameter(name = 'c8leu2HDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leu2HDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 613 ])

c8led2HDx1Re = Parameter(name = 'c8led2HDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8led2HDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 614 ])

c8led2HDx1Im = Parameter(name = 'c8led2HDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8led2HDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 615 ])

c8led2HDx2Re = Parameter(name = 'c8led2HDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8led2HDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 616 ])

c8led2HDx2Im = Parameter(name = 'c8led2HDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8led2HDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 617 ])

c8led2HDx3Re = Parameter(name = 'c8led2HDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8led2HDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 618 ])

c8led2HDx3Im = Parameter(name = 'c8led2HDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8led2HDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 619 ])

c8leudHDx1Re = Parameter(name = 'c8leudHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leudHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 620 ])

c8leudHDx1Im = Parameter(name = 'c8leudHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leudHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 621 ])

c8leudHDx2Re = Parameter(name = 'c8leudHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leudHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 622 ])

c8leudHDx2Im = Parameter(name = 'c8leudHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leudHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 623 ])

c8leudHDx3Re = Parameter(name = 'c8leudHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leudHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 624 ])

c8leudHDx3Im = Parameter(name = 'c8leudHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8leudHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 625 ])

c8le3HDx2Re = Parameter(name = 'c8le3HDx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8le3HDx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 626 ])

c8le3HDx2Im = Parameter(name = 'c8le3HDx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8le3HDx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 627 ])

c8l2quHDx1Re = Parameter(name = 'c8l2quHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 628 ])

c8l2quHDx1Im = Parameter(name = 'c8l2quHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 629 ])

c8l2quHDx2Re = Parameter(name = 'c8l2quHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 630 ])

c8l2quHDx2Im = Parameter(name = 'c8l2quHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 631 ])

c8l2quHDx3Re = Parameter(name = 'c8l2quHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 632 ])

c8l2quHDx3Im = Parameter(name = 'c8l2quHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 633 ])

c8l2quHDx4Re = Parameter(name = 'c8l2quHDx4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 634 ])

c8l2quHDx4Im = Parameter(name = 'c8l2quHDx4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 635 ])

c8l2quHDx5Re = Parameter(name = 'c8l2quHDx5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 636 ])

c8l2quHDx5Im = Parameter(name = 'c8l2quHDx5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 637 ])

c8l2quHDx6Re = Parameter(name = 'c8l2quHDx6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 638 ])

c8l2quHDx6Im = Parameter(name = 'c8l2quHDx6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2quHDx6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 639 ])

c8e2quHDx1Re = Parameter(name = 'c8e2quHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2quHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 640 ])

c8e2quHDx1Im = Parameter(name = 'c8e2quHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2quHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 641 ])

c8e2quHDx2Re = Parameter(name = 'c8e2quHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2quHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 642 ])

c8e2quHDx2Im = Parameter(name = 'c8e2quHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2quHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 643 ])

c8e2quHDx3Re = Parameter(name = 'c8e2quHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2quHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 644 ])

c8e2quHDx3Im = Parameter(name = 'c8e2quHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2quHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 645 ])

c8q3uHDx1Re = Parameter(name = 'c8q3uHDx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 646 ])

c8q3uHDx1Im = Parameter(name = 'c8q3uHDx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 647 ])

c8q3uHDx2Re = Parameter(name = 'c8q3uHDx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 648 ])

c8q3uHDx2Im = Parameter(name = 'c8q3uHDx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 649 ])

c8q3uHDx3Re = Parameter(name = 'c8q3uHDx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 650 ])

c8q3uHDx3Im = Parameter(name = 'c8q3uHDx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 651 ])

c8q3uHDx4Re = Parameter(name = 'c8q3uHDx4Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx4Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 652 ])

c8q3uHDx4Im = Parameter(name = 'c8q3uHDx4Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx4Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 653 ])

c8q3uHDx5Re = Parameter(name = 'c8q3uHDx5Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx5Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 654 ])

c8q3uHDx5Im = Parameter(name = 'c8q3uHDx5Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx5Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 655 ])

c8q3uHDx6Re = Parameter(name = 'c8q3uHDx6Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx6Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 656 ])

c8q3uHDx6Im = Parameter(name = 'c8q3uHDx6Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3uHDx6Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 657 ])

c8qu3HDx1Re = Parameter(name = 'c8qu3HDx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qu3HDx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 658 ])

c8qu3HDx1Im = Parameter(name = 'c8qu3HDx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qu3HDx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 659 ])

c8qu3HDx2Re = Parameter(name = 'c8qu3HDx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qu3HDx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 660 ])

c8qu3HDx2Im = Parameter(name = 'c8qu3HDx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qu3HDx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 661 ])

c8qu3HDx3Re = Parameter(name = 'c8qu3HDx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qu3HDx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 662 ])

c8qu3HDx3Im = Parameter(name = 'c8qu3HDx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qu3HDx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 663 ])

c8qud2HDx1Re = Parameter(name = 'c8qud2HDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 664 ])

c8qud2HDx1Im = Parameter(name = 'c8qud2HDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 665 ])

c8qud2HDx2Re = Parameter(name = 'c8qud2HDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 666 ])

c8qud2HDx2Im = Parameter(name = 'c8qud2HDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 667 ])

c8qud2HDx3Re = Parameter(name = 'c8qud2HDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 668 ])

c8qud2HDx3Im = Parameter(name = 'c8qud2HDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 669 ])

c8qud2HDx4Re = Parameter(name = 'c8qud2HDx4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 670 ])

c8qud2HDx4Im = Parameter(name = 'c8qud2HDx4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 671 ])

c8qud2HDx5Re = Parameter(name = 'c8qud2HDx5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 672 ])

c8qud2HDx5Im = Parameter(name = 'c8qud2HDx5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 673 ])

c8qud2HDx6Re = Parameter(name = 'c8qud2HDx6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 674 ])

c8qud2HDx6Im = Parameter(name = 'c8qud2HDx6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qud2HDx6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 675 ])

c8l2qdHDx1Re = Parameter(name = 'c8l2qdHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 676 ])

c8l2qdHDx1Im = Parameter(name = 'c8l2qdHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 677 ])

c8l2qdHDx2Re = Parameter(name = 'c8l2qdHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 678 ])

c8l2qdHDx2Im = Parameter(name = 'c8l2qdHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 679 ])

c8l2qdHDx3Re = Parameter(name = 'c8l2qdHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 680 ])

c8l2qdHDx3Im = Parameter(name = 'c8l2qdHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 681 ])

c8l2qdHDx4Re = Parameter(name = 'c8l2qdHDx4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 682 ])

c8l2qdHDx4Im = Parameter(name = 'c8l2qdHDx4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 683 ])

c8l2qdHDx5Re = Parameter(name = 'c8l2qdHDx5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 684 ])

c8l2qdHDx5Im = Parameter(name = 'c8l2qdHDx5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 685 ])

c8l2qdHDx6Re = Parameter(name = 'c8l2qdHDx6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 686 ])

c8l2qdHDx6Im = Parameter(name = 'c8l2qdHDx6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8l2qdHDx6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 687 ])

c8e2qdHDx1Re = Parameter(name = 'c8e2qdHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2qdHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 688 ])

c8e2qdHDx1Im = Parameter(name = 'c8e2qdHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2qdHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 689 ])

c8e2qdHDx2Re = Parameter(name = 'c8e2qdHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2qdHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 690 ])

c8e2qdHDx2Im = Parameter(name = 'c8e2qdHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2qdHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 691 ])

c8e2qdHDx3Re = Parameter(name = 'c8e2qdHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2qdHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 692 ])

c8e2qdHDx3Im = Parameter(name = 'c8e2qdHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8e2qdHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 693 ])

c8q3dHDx1Re = Parameter(name = 'c8q3dHDx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 694 ])

c8q3dHDx1Im = Parameter(name = 'c8q3dHDx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 695 ])

c8q3dHDx2Re = Parameter(name = 'c8q3dHDx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 696 ])

c8q3dHDx2Im = Parameter(name = 'c8q3dHDx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 697 ])

c8q3dHDx3Re = Parameter(name = 'c8q3dHDx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 698 ])

c8q3dHDx3Im = Parameter(name = 'c8q3dHDx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 699 ])

c8q3dHDx4Re = Parameter(name = 'c8q3dHDx4Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx4Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 700 ])

c8q3dHDx4Im = Parameter(name = 'c8q3dHDx4Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx4Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 701 ])

c8q3dHDx5Re = Parameter(name = 'c8q3dHDx5Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx5Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 702 ])

c8q3dHDx5Im = Parameter(name = 'c8q3dHDx5Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx5Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 703 ])

c8q3dHDx6Re = Parameter(name = 'c8q3dHDx6Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx6Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 704 ])

c8q3dHDx6Im = Parameter(name = 'c8q3dHDx6Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8q3dHDx6Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 705 ])

c8qu2dHDx1Re = Parameter(name = 'c8qu2dHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 706 ])

c8qu2dHDx1Im = Parameter(name = 'c8qu2dHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 707 ])

c8qu2dHDx2Re = Parameter(name = 'c8qu2dHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 708 ])

c8qu2dHDx2Im = Parameter(name = 'c8qu2dHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 709 ])

c8qu2dHDx3Re = Parameter(name = 'c8qu2dHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 710 ])

c8qu2dHDx3Im = Parameter(name = 'c8qu2dHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 711 ])

c8qu2dHDx4Re = Parameter(name = 'c8qu2dHDx4Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx4Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 712 ])

c8qu2dHDx4Im = Parameter(name = 'c8qu2dHDx4Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx4Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 713 ])

c8qu2dHDx5Re = Parameter(name = 'c8qu2dHDx5Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx5Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 714 ])

c8qu2dHDx5Im = Parameter(name = 'c8qu2dHDx5Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx5Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 715 ])

c8qu2dHDx6Re = Parameter(name = 'c8qu2dHDx6Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx6Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 716 ])

c8qu2dHDx6Im = Parameter(name = 'c8qu2dHDx6Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8qu2dHDx6Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 717 ])

c8qd3HDx1Re = Parameter(name = 'c8qd3HDx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qd3HDx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 718 ])

c8qd3HDx1Im = Parameter(name = 'c8qd3HDx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qd3HDx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 719 ])

c8qd3HDx2Re = Parameter(name = 'c8qd3HDx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qd3HDx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 720 ])

c8qd3HDx2Im = Parameter(name = 'c8qd3HDx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qd3HDx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 721 ])

c8qd3HDx3Re = Parameter(name = 'c8qd3HDx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qd3HDx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 722 ])

c8qd3HDx3Im = Parameter(name = 'c8qd3HDx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qd3HDx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 723 ])

c8l4D2x1 = Parameter(name = 'c8l4D2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{l4D2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 724 ])

c8l4D2x2 = Parameter(name = 'c8l4D2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{l4D2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 725 ])

c8q4D2x1 = Parameter(name = 'c8q4D2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{q4D2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 726 ])

c8q4D2x2 = Parameter(name = 'c8q4D2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{q4D2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 727 ])

c8q4D2x3 = Parameter(name = 'c8q4D2x3',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{q4D2x3}}',
                     lhablock = 'DIM8',
                     lhacode = [ 728 ])

c8q4D2x4 = Parameter(name = 'c8q4D2x4',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{q4D2x4}}',
                     lhablock = 'DIM8',
                     lhacode = [ 729 ])

c8l2q2D2x1 = Parameter(name = 'c8l2q2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 730 ])

c8l2q2D2x2 = Parameter(name = 'c8l2q2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 731 ])

c8l2q2D2x3 = Parameter(name = 'c8l2q2D2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2D2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 732 ])

c8l2q2D2x4 = Parameter(name = 'c8l2q2D2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2q2D2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 733 ])

c8e4D2 = Parameter(name = 'c8e4D2',
                   nature = 'external',
                   type = 'real',
                   value = 0,
                   texname = 'c_{8 \\text{e4D2}}',
                   lhablock = 'DIM8',
                   lhacode = [ 734 ])

c8u4D2x1 = Parameter(name = 'c8u4D2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{u4D2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 735 ])

c8u4D2x2 = Parameter(name = 'c8u4D2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{u4D2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 736 ])

c8d4D2x1 = Parameter(name = 'c8d4D2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{d4D2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 737 ])

c8d4D2x2 = Parameter(name = 'c8d4D2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{d4D2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 738 ])

c8e2u2D2x1 = Parameter(name = 'c8e2u2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2u2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 739 ])

c8e2u2D2x2 = Parameter(name = 'c8e2u2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2u2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 740 ])

c8e2d2D2x1 = Parameter(name = 'c8e2d2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2d2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 741 ])

c8e2d2D2x2 = Parameter(name = 'c8e2d2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{e2d2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 742 ])

c8u2d2D2x1 = Parameter(name = 'c8u2d2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2d2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 743 ])

c8u2d2D2x2 = Parameter(name = 'c8u2d2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2d2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 744 ])

c8u2d2D2x3 = Parameter(name = 'c8u2d2D2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2d2D2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 745 ])

c8u2d2D2x4 = Parameter(name = 'c8u2d2D2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{u2d2D2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 746 ])

c8l2e2D2x1 = Parameter(name = 'c8l2e2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2e2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 747 ])

c8l2e2D2x2 = Parameter(name = 'c8l2e2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2e2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 748 ])

c8l2u2D2x1 = Parameter(name = 'c8l2u2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2u2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 749 ])

c8l2u2D2x2 = Parameter(name = 'c8l2u2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2u2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 750 ])

c8l2d2D2x1 = Parameter(name = 'c8l2d2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2d2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 751 ])

c8l2d2D2x2 = Parameter(name = 'c8l2d2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{l2d2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 752 ])

c8q2e2D2x1 = Parameter(name = 'c8q2e2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2e2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 753 ])

c8q2e2D2x2 = Parameter(name = 'c8q2e2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2e2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 754 ])

c8q2u2D2x1 = Parameter(name = 'c8q2u2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2u2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 755 ])

c8q2u2D2x2 = Parameter(name = 'c8q2u2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2u2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 756 ])

c8q2u2D2x3 = Parameter(name = 'c8q2u2D2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2u2D2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 757 ])

c8q2u2D2x4 = Parameter(name = 'c8q2u2D2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2u2D2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 758 ])

c8q2d2D2x1 = Parameter(name = 'c8q2d2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2d2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 759 ])

c8q2d2D2x2 = Parameter(name = 'c8q2d2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2d2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 760 ])

c8q2d2D2x3 = Parameter(name = 'c8q2d2D2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2d2D2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 761 ])

c8q2d2D2x4 = Parameter(name = 'c8q2d2D2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{q2d2D2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 762 ])

c8q2udD2x1Re = Parameter(name = 'c8q2udD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 763 ])

c8q2udD2x1Im = Parameter(name = 'c8q2udD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 764 ])

c8q2udD2x2Re = Parameter(name = 'c8q2udD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 765 ])

c8q2udD2x2Im = Parameter(name = 'c8q2udD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 766 ])

c8q2udD2x3Re = Parameter(name = 'c8q2udD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 767 ])

c8q2udD2x3Im = Parameter(name = 'c8q2udD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8q2udD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 768 ])

c8lequD2x1Re = Parameter(name = 'c8lequD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 769 ])

c8lequD2x1Im = Parameter(name = 'c8lequD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 770 ])

c8lequD2x2Re = Parameter(name = 'c8lequD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 771 ])

c8lequD2x2Im = Parameter(name = 'c8lequD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 772 ])

c8lequD2x3Re = Parameter(name = 'c8lequD2x3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequD2x3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 773 ])

c8lequD2x3Im = Parameter(name = 'c8lequD2x3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lequD2x3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 774 ])

c8G3H2x1 = Parameter(name = 'c8G3H2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G3H2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 775 ])

c8G3H2x2 = Parameter(name = 'c8G3H2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G3H2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 776 ])

c8W3H2x1 = Parameter(name = 'c8W3H2x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W3H2x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 777 ])

c8W3H2x2 = Parameter(name = 'c8W3H2x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W3H2x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 778 ])

c8W2BH2x1 = Parameter(name = 'c8W2BH2x1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{W2BH2x1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 779 ])

c8W2BH2x2 = Parameter(name = 'c8W2BH2x2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{W2BH2x2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 780 ])

c8G2H4x1 = Parameter(name = 'c8G2H4x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2H4x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 781 ])

c8G2H4x2 = Parameter(name = 'c8G2H4x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{G2H4x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 782 ])

c8W2H4x1 = Parameter(name = 'c8W2H4x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2H4x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 783 ])

c8W2H4x2 = Parameter(name = 'c8W2H4x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2H4x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 784 ])

c8W2H4x3 = Parameter(name = 'c8W2H4x3',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2H4x3}}',
                     lhablock = 'DIM8',
                     lhacode = [ 785 ])

c8W2H4x4 = Parameter(name = 'c8W2H4x4',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{W2H4x4}}',
                     lhablock = 'DIM8',
                     lhacode = [ 786 ])

c8WBH4x1 = Parameter(name = 'c8WBH4x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{WBH4x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 787 ])

c8WBH4x2 = Parameter(name = 'c8WBH4x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{WBH4x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 788 ])

c8B2H4x1 = Parameter(name = 'c8B2H4x1',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{B2H4x1}}',
                     lhablock = 'DIM8',
                     lhacode = [ 789 ])

c8B2H4x2 = Parameter(name = 'c8B2H4x2',
                     nature = 'external',
                     type = 'real',
                     value = 0,
                     texname = 'c_{8 \\text{B2H4x2}}',
                     lhablock = 'DIM8',
                     lhacode = [ 790 ])

c8G2H2D2x1 = Parameter(name = 'c8G2H2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{G2H2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 791 ])

c8G2H2D2x2 = Parameter(name = 'c8G2H2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{G2H2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 792 ])

c8G2H2D2x3 = Parameter(name = 'c8G2H2D2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{G2H2D2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 793 ])

c8W2H2D2x1 = Parameter(name = 'c8W2H2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{W2H2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 794 ])

c8W2H2D2x2 = Parameter(name = 'c8W2H2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{W2H2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 795 ])

c8W2H2D2x3 = Parameter(name = 'c8W2H2D2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{W2H2D2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 796 ])

c8W2H2D2x4 = Parameter(name = 'c8W2H2D2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{W2H2D2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 797 ])

c8W2H2D2x5 = Parameter(name = 'c8W2H2D2x5',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{W2H2D2x5}}',
                       lhablock = 'DIM8',
                       lhacode = [ 798 ])

c8W2H2D2x6 = Parameter(name = 'c8W2H2D2x6',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{W2H2D2x6}}',
                       lhablock = 'DIM8',
                       lhacode = [ 799 ])

c8WBH2D2x1 = Parameter(name = 'c8WBH2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{WBH2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 800 ])

c8WBH2D2x2 = Parameter(name = 'c8WBH2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{WBH2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 801 ])

c8WBH2D2x3 = Parameter(name = 'c8WBH2D2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{WBH2D2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 802 ])

c8WBH2D2x4 = Parameter(name = 'c8WBH2D2x4',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{WBH2D2x4}}',
                       lhablock = 'DIM8',
                       lhacode = [ 803 ])

c8WBH2D2x5 = Parameter(name = 'c8WBH2D2x5',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{WBH2D2x5}}',
                       lhablock = 'DIM8',
                       lhacode = [ 804 ])

c8WBH2D2x6 = Parameter(name = 'c8WBH2D2x6',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{WBH2D2x6}}',
                       lhablock = 'DIM8',
                       lhacode = [ 805 ])

c8B2H2D2x1 = Parameter(name = 'c8B2H2D2x1',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{B2H2D2x1}}',
                       lhablock = 'DIM8',
                       lhacode = [ 806 ])

c8B2H2D2x2 = Parameter(name = 'c8B2H2D2x2',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{B2H2D2x2}}',
                       lhablock = 'DIM8',
                       lhacode = [ 807 ])

c8B2H2D2x3 = Parameter(name = 'c8B2H2D2x3',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = 'c_{8 \\text{B2H2D2x3}}',
                       lhablock = 'DIM8',
                       lhacode = [ 808 ])

c8WH4D2x1 = Parameter(name = 'c8WH4D2x1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{WH4D2x1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 809 ])

c8WH4D2x2 = Parameter(name = 'c8WH4D2x2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{WH4D2x2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 810 ])

c8WH4D2x3 = Parameter(name = 'c8WH4D2x3',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{WH4D2x3}}',
                      lhablock = 'DIM8',
                      lhacode = [ 811 ])

c8WH4D2x4 = Parameter(name = 'c8WH4D2x4',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{WH4D2x4}}',
                      lhablock = 'DIM8',
                      lhacode = [ 812 ])

c8BH4D2x1 = Parameter(name = 'c8BH4D2x1',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{BH4D2x1}}',
                      lhablock = 'DIM8',
                      lhacode = [ 813 ])

c8BH4D2x2 = Parameter(name = 'c8BH4D2x2',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = 'c_{8 \\text{BH4D2x2}}',
                      lhablock = 'DIM8',
                      lhacode = [ 814 ])

c8leG2Hx1Re = Parameter(name = 'c8leG2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leG2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 815 ])

c8leG2Hx1Im = Parameter(name = 'c8leG2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leG2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 816 ])

c8leG2Hx2Re = Parameter(name = 'c8leG2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leG2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 817 ])

c8leG2Hx2Im = Parameter(name = 'c8leG2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leG2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 818 ])

c8leW2Hx1Re = Parameter(name = 'c8leW2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leW2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 819 ])

c8leW2Hx1Im = Parameter(name = 'c8leW2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leW2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 820 ])

c8leW2Hx2Re = Parameter(name = 'c8leW2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leW2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 821 ])

c8leW2Hx2Im = Parameter(name = 'c8leW2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leW2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 822 ])

c8leW2Hx3Re = Parameter(name = 'c8leW2Hx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leW2Hx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 823 ])

c8leW2Hx3Im = Parameter(name = 'c8leW2Hx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leW2Hx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 824 ])

c8quG2Hx1Re = Parameter(name = 'c8quG2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 825 ])

c8quG2Hx1Im = Parameter(name = 'c8quG2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 826 ])

c8quG2Hx2Re = Parameter(name = 'c8quG2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 827 ])

c8quG2Hx2Im = Parameter(name = 'c8quG2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 828 ])

c8quG2Hx3Re = Parameter(name = 'c8quG2Hx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 829 ])

c8quG2Hx3Im = Parameter(name = 'c8quG2Hx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 830 ])

c8quG2Hx4Re = Parameter(name = 'c8quG2Hx4Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx4Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 831 ])

c8quG2Hx4Im = Parameter(name = 'c8quG2Hx4Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx4Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 832 ])

c8quG2Hx5Re = Parameter(name = 'c8quG2Hx5Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx5Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 833 ])

c8quG2Hx5Im = Parameter(name = 'c8quG2Hx5Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quG2Hx5Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 834 ])

c8quGWHx1Re = Parameter(name = 'c8quGWHx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGWHx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 835 ])

c8quGWHx1Im = Parameter(name = 'c8quGWHx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGWHx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 836 ])

c8quGWHx2Re = Parameter(name = 'c8quGWHx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGWHx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 837 ])

c8quGWHx2Im = Parameter(name = 'c8quGWHx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGWHx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 838 ])

c8quGWHx3Re = Parameter(name = 'c8quGWHx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGWHx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 839 ])

c8quGWHx3Im = Parameter(name = 'c8quGWHx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGWHx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 840 ])

c8quGBHx1Re = Parameter(name = 'c8quGBHx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGBHx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 841 ])

c8quGBHx1Im = Parameter(name = 'c8quGBHx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGBHx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 842 ])

c8quGBHx2Re = Parameter(name = 'c8quGBHx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGBHx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 843 ])

c8quGBHx2Im = Parameter(name = 'c8quGBHx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGBHx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 844 ])

c8quGBHx3Re = Parameter(name = 'c8quGBHx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGBHx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 845 ])

c8quGBHx3Im = Parameter(name = 'c8quGBHx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quGBHx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 846 ])

c8quW2Hx1Re = Parameter(name = 'c8quW2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quW2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 847 ])

c8quW2Hx1Im = Parameter(name = 'c8quW2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quW2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 848 ])

c8quW2Hx2Re = Parameter(name = 'c8quW2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quW2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 849 ])

c8quW2Hx2Im = Parameter(name = 'c8quW2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quW2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 850 ])

c8quW2Hx3Re = Parameter(name = 'c8quW2Hx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quW2Hx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 851 ])

c8quW2Hx3Im = Parameter(name = 'c8quW2Hx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quW2Hx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 852 ])

c8quWBHx3Re = Parameter(name = 'c8quWBHx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWBHx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 853 ])

c8quWBHx3Im = Parameter(name = 'c8quWBHx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWBHx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 854 ])

c8quWBHx1Re = Parameter(name = 'c8quWBHx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWBHx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 855 ])

c8quWBHx1Im = Parameter(name = 'c8quWBHx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWBHx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 856 ])

c8quWBHx2Re = Parameter(name = 'c8quWBHx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWBHx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 857 ])

c8quWBHx2Im = Parameter(name = 'c8quWBHx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quWBHx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 858 ])

c8quB2Hx1Re = Parameter(name = 'c8quB2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quB2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 859 ])

c8quB2Hx1Im = Parameter(name = 'c8quB2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quB2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 860 ])

c8quB2Hx2Re = Parameter(name = 'c8quB2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quB2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 861 ])

c8quB2Hx2Im = Parameter(name = 'c8quB2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8quB2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 862 ])

c8leWBHx1Re = Parameter(name = 'c8leWBHx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWBHx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 863 ])

c8leWBHx1Im = Parameter(name = 'c8leWBHx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWBHx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 864 ])

c8leWBHx2Re = Parameter(name = 'c8leWBHx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWBHx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 865 ])

c8leWBHx2Im = Parameter(name = 'c8leWBHx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWBHx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 866 ])

c8leWBHx3Re = Parameter(name = 'c8leWBHx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWBHx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 867 ])

c8leWBHx3Im = Parameter(name = 'c8leWBHx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leWBHx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 868 ])

c8leB2Hx1Re = Parameter(name = 'c8leB2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leB2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 869 ])

c8leB2Hx1Im = Parameter(name = 'c8leB2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leB2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 870 ])

c8leB2Hx2Re = Parameter(name = 'c8leB2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leB2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 871 ])

c8leB2Hx2Im = Parameter(name = 'c8leB2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8leB2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 872 ])

c8qdG2Hx1Re = Parameter(name = 'c8qdG2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 873 ])

c8qdG2Hx1Im = Parameter(name = 'c8qdG2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 874 ])

c8qdG2Hx2Re = Parameter(name = 'c8qdG2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 875 ])

c8qdG2Hx2Im = Parameter(name = 'c8qdG2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 876 ])

c8qdG2Hx3Re = Parameter(name = 'c8qdG2Hx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 877 ])

c8qdG2Hx3Im = Parameter(name = 'c8qdG2Hx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 878 ])

c8qdG2Hx4Re = Parameter(name = 'c8qdG2Hx4Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx4Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 879 ])

c8qdG2Hx4Im = Parameter(name = 'c8qdG2Hx4Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx4Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 880 ])

c8qdG2Hx5Re = Parameter(name = 'c8qdG2Hx5Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx5Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 881 ])

c8qdG2Hx5Im = Parameter(name = 'c8qdG2Hx5Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdG2Hx5Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 882 ])

c8qdGWHx1Re = Parameter(name = 'c8qdGWHx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGWHx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 883 ])

c8qdGWHx1Im = Parameter(name = 'c8qdGWHx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGWHx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 884 ])

c8qdGWHx2Re = Parameter(name = 'c8qdGWHx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGWHx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 885 ])

c8qdGWHx2Im = Parameter(name = 'c8qdGWHx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGWHx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 886 ])

c8qdGWHx3Re = Parameter(name = 'c8qdGWHx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGWHx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 887 ])

c8qdGWHx3Im = Parameter(name = 'c8qdGWHx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGWHx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 888 ])

c8qdGBHx1Re = Parameter(name = 'c8qdGBHx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGBHx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 889 ])

c8qdGBHx1Im = Parameter(name = 'c8qdGBHx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGBHx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 890 ])

c8qdGBHx2Re = Parameter(name = 'c8qdGBHx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGBHx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 891 ])

c8qdGBHx2Im = Parameter(name = 'c8qdGBHx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGBHx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 892 ])

c8qdGBHx3Re = Parameter(name = 'c8qdGBHx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGBHx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 893 ])

c8qdGBHx3Im = Parameter(name = 'c8qdGBHx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdGBHx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 894 ])

c8qdW2Hx1Re = Parameter(name = 'c8qdW2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdW2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 895 ])

c8qdW2Hx1Im = Parameter(name = 'c8qdW2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdW2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 896 ])

c8qdW2Hx2Re = Parameter(name = 'c8qdW2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdW2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 897 ])

c8qdW2Hx2Im = Parameter(name = 'c8qdW2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdW2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 898 ])

c8qdW2Hx3Re = Parameter(name = 'c8qdW2Hx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdW2Hx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 899 ])

c8qdW2Hx3Im = Parameter(name = 'c8qdW2Hx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdW2Hx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 900 ])

c8qdWBHx1Re = Parameter(name = 'c8qdWBHx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWBHx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 901 ])

c8qdWBHx1Im = Parameter(name = 'c8qdWBHx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWBHx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 902 ])

c8qdWBHx2Re = Parameter(name = 'c8qdWBHx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWBHx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 903 ])

c8qdWBHx2Im = Parameter(name = 'c8qdWBHx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWBHx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 904 ])

c8qdWBHx3Re = Parameter(name = 'c8qdWBHx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWBHx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 905 ])

c8qdWBHx3Im = Parameter(name = 'c8qdWBHx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdWBHx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 906 ])

c8qdB2Hx1Re = Parameter(name = 'c8qdB2Hx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdB2Hx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 907 ])

c8qdB2Hx1Im = Parameter(name = 'c8qdB2Hx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdB2Hx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 908 ])

c8qdB2Hx2Re = Parameter(name = 'c8qdB2Hx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdB2Hx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 909 ])

c8qdB2Hx2Im = Parameter(name = 'c8qdB2Hx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8qdB2Hx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 910 ])

c8lqudH2x1Re = Parameter(name = 'c8lqudH2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lqudH2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 911 ])

c8lqudH2x1Im = Parameter(name = 'c8lqudH2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lqudH2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 912 ])

c8lqudH2x2Re = Parameter(name = 'c8lqudH2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lqudH2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 913 ])

c8lqudH2x2Im = Parameter(name = 'c8lqudH2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lqudH2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 914 ])

c8eq2uH2Re = Parameter(name = 'c8eq2uH2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8eq2uH2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 915 ])

c8eq2uH2Im = Parameter(name = 'c8eq2uH2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8eq2uH2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 916 ])

c8lq3H2x1Re = Parameter(name = 'c8lq3H2x1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lq3H2x1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 917 ])

c8lq3H2x1Im = Parameter(name = 'c8lq3H2x1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lq3H2x1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 918 ])

c8lq3H2x2Re = Parameter(name = 'c8lq3H2x2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lq3H2x2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 919 ])

c8lq3H2x2Im = Parameter(name = 'c8lq3H2x2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lq3H2x2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 920 ])

c8eu2dH2Re = Parameter(name = 'c8eu2dH2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8eu2dH2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 921 ])

c8eu2dH2Im = Parameter(name = 'c8eu2dH2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8eu2dH2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 922 ])

c8lq3H2x3Re = Parameter(name = 'c8lq3H2x3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lq3H2x3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 923 ])

c8lq3H2x3Im = Parameter(name = 'c8lq3H2x3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lq3H2x3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 924 ])

c8lqu2H2Re = Parameter(name = 'c8lqu2H2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lqu2H2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 925 ])

c8lqu2H2Im = Parameter(name = 'c8lqu2H2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lqu2H2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 926 ])

c8lqd2H2Re = Parameter(name = 'c8lqd2H2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lqd2H2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 927 ])

c8lqd2H2Im = Parameter(name = 'c8lqd2H2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lqd2H2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 928 ])

c8eq2dH2Re = Parameter(name = 'c8eq2dH2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8eq2dH2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 929 ])

c8eq2dH2Im = Parameter(name = 'c8eq2dH2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8eq2dH2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 930 ])

c8lqudD2x1Re = Parameter(name = 'c8lqudD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lqudD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 931 ])

c8lqudD2x1Im = Parameter(name = 'c8lqudD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lqudD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 932 ])

c8lqudD2x2Re = Parameter(name = 'c8lqudD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lqudD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 933 ])

c8lqudD2x2Im = Parameter(name = 'c8lqudD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lqudD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 934 ])

c8eq2uD2Re = Parameter(name = 'c8eq2uD2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8eq2uD2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 935 ])

c8eq2uD2Im = Parameter(name = 'c8eq2uD2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8eq2uD2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 936 ])

c8lq3D2Re = Parameter(name = 'c8lq3D2Re',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8lq3D2Re}',
                      lhablock = 'DIM8',
                      lhacode = [ 937 ])

c8lq3D2Im = Parameter(name = 'c8lq3D2Im',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8lq3D2Im}',
                      lhablock = 'DIM8',
                      lhacode = [ 938 ])

c8eu2dD2x1Re = Parameter(name = 'c8eu2dD2x1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8eu2dD2x1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 939 ])

c8eu2dD2x1Im = Parameter(name = 'c8eu2dD2x1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8eu2dD2x1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 940 ])

c8eu2dD2x2Re = Parameter(name = 'c8eu2dD2x2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8eu2dD2x2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 941 ])

c8eu2dD2x2Im = Parameter(name = 'c8eu2dD2x2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8eu2dD2x2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 942 ])

c8lqudGx1Re = Parameter(name = 'c8lqudGx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudGx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 943 ])

c8lqudGx1Im = Parameter(name = 'c8lqudGx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudGx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 944 ])

c8lqudGx2Re = Parameter(name = 'c8lqudGx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudGx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 945 ])

c8lqudGx2Im = Parameter(name = 'c8lqudGx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudGx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 946 ])

c8lqudGx3Re = Parameter(name = 'c8lqudGx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudGx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 947 ])

c8lqudGx3Im = Parameter(name = 'c8lqudGx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudGx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 948 ])

c8lqudGx4Re = Parameter(name = 'c8lqudGx4Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudGx4Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 949 ])

c8lqudGx4Im = Parameter(name = 'c8lqudGx4Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudGx4Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 950 ])

c8lqudWx1Re = Parameter(name = 'c8lqudWx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudWx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 951 ])

c8lqudWx1Im = Parameter(name = 'c8lqudWx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudWx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 952 ])

c8lqudWx2Re = Parameter(name = 'c8lqudWx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudWx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 953 ])

c8lqudWx2Im = Parameter(name = 'c8lqudWx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudWx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 954 ])

c8lqudBx1Re = Parameter(name = 'c8lqudBx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudBx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 955 ])

c8lqudBx1Im = Parameter(name = 'c8lqudBx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudBx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 956 ])

c8lqudBx2Re = Parameter(name = 'c8lqudBx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudBx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 957 ])

c8lqudBx2Im = Parameter(name = 'c8lqudBx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8lqudBx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 958 ])

c8eq2uGx1Re = Parameter(name = 'c8eq2uGx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uGx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 959 ])

c8eq2uGx1Im = Parameter(name = 'c8eq2uGx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uGx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 960 ])

c8eq2uGx2Re = Parameter(name = 'c8eq2uGx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uGx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 961 ])

c8eq2uGx2Im = Parameter(name = 'c8eq2uGx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uGx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 962 ])

c8eq2uWx1Re = Parameter(name = 'c8eq2uWx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uWx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 963 ])

c8eq2uWx1Im = Parameter(name = 'c8eq2uWx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uWx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 964 ])

c8eq2uBx1Re = Parameter(name = 'c8eq2uBx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uBx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 965 ])

c8eq2uBx1Im = Parameter(name = 'c8eq2uBx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uBx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 966 ])

c8lq3Gx1Re = Parameter(name = 'c8lq3Gx1Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Gx1Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 967 ])

c8lq3Gx1Im = Parameter(name = 'c8lq3Gx1Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Gx1Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 968 ])

c8lq3Gx2Re = Parameter(name = 'c8lq3Gx2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Gx2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 969 ])

c8lq3Gx2Im = Parameter(name = 'c8lq3Gx2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Gx2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 970 ])

c8lq3Wx1Re = Parameter(name = 'c8lq3Wx1Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Wx1Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 971 ])

c8lq3Wx1Im = Parameter(name = 'c8lq3Wx1Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Wx1Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 972 ])

c8lq3Wx2Re = Parameter(name = 'c8lq3Wx2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Wx2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 973 ])

c8lq3Wx2Im = Parameter(name = 'c8lq3Wx2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Wx2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 974 ])

c8lq3Bx1Re = Parameter(name = 'c8lq3Bx1Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Bx1Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 975 ])

c8lq3Bx1Im = Parameter(name = 'c8lq3Bx1Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Bx1Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 976 ])

c8eu2dGx1Re = Parameter(name = 'c8eu2dGx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dGx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 977 ])

c8eu2dGx1Im = Parameter(name = 'c8eu2dGx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dGx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 978 ])

c8eu2dGx2Re = Parameter(name = 'c8eu2dGx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dGx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 979 ])

c8eu2dGx2Im = Parameter(name = 'c8eu2dGx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dGx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 980 ])

c8eu2dGx3Re = Parameter(name = 'c8eu2dGx3Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dGx3Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 981 ])

c8eu2dGx3Im = Parameter(name = 'c8eu2dGx3Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dGx3Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 982 ])

c8eu2dBx1Re = Parameter(name = 'c8eu2dBx1Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dBx1Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 983 ])

c8eu2dBx1Im = Parameter(name = 'c8eu2dBx1Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dBx1Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 984 ])

c8eu2dBx2Re = Parameter(name = 'c8eu2dBx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dBx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 985 ])

c8eu2dBx2Im = Parameter(name = 'c8eu2dBx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eu2dBx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 986 ])

c8eq2uWx2Re = Parameter(name = 'c8eq2uWx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uWx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 987 ])

c8eq2uWx2Im = Parameter(name = 'c8eq2uWx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uWx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 988 ])

c8eq2uBx2Re = Parameter(name = 'c8eq2uBx2Re',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uBx2Re}',
                        lhablock = 'DIM8',
                        lhacode = [ 989 ])

c8eq2uBx2Im = Parameter(name = 'c8eq2uBx2Im',
                        nature = 'external',
                        type = 'real',
                        value = 0,
                        texname = '\\text{c8eq2uBx2Im}',
                        lhablock = 'DIM8',
                        lhacode = [ 990 ])

c8lq3Gx3Re = Parameter(name = 'c8lq3Gx3Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Gx3Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 991 ])

c8lq3Gx3Im = Parameter(name = 'c8lq3Gx3Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Gx3Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 992 ])

c8lq3Gx4Re = Parameter(name = 'c8lq3Gx4Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Gx4Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 993 ])

c8lq3Gx4Im = Parameter(name = 'c8lq3Gx4Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Gx4Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 994 ])

c8lq3Wx3Re = Parameter(name = 'c8lq3Wx3Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Wx3Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 995 ])

c8lq3Wx3Im = Parameter(name = 'c8lq3Wx3Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Wx3Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 996 ])

c8lq3Bx2Re = Parameter(name = 'c8lq3Bx2Re',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Bx2Re}',
                       lhablock = 'DIM8',
                       lhacode = [ 997 ])

c8lq3Bx2Im = Parameter(name = 'c8lq3Bx2Im',
                       nature = 'external',
                       type = 'real',
                       value = 0,
                       texname = '\\text{c8lq3Bx2Im}',
                       lhablock = 'DIM8',
                       lhacode = [ 998 ])

c8lu2dHDx1Re = Parameter(name = 'c8lu2dHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lu2dHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 999 ])

c8lu2dHDx1Im = Parameter(name = 'c8lu2dHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lu2dHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1000 ])

c8lu2dHDx2Re = Parameter(name = 'c8lu2dHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lu2dHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1001 ])

c8lu2dHDx2Im = Parameter(name = 'c8lu2dHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lu2dHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1002 ])

c8lud2HDx1Re = Parameter(name = 'c8lud2HDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lud2HDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1003 ])

c8lud2HDx1Im = Parameter(name = 'c8lud2HDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lud2HDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1004 ])

c8lud2HDx2Re = Parameter(name = 'c8lud2HDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lud2HDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1005 ])

c8lud2HDx2Im = Parameter(name = 'c8lud2HDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lud2HDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1006 ])

c8lq2uHDx1Re = Parameter(name = 'c8lq2uHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2uHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1007 ])

c8lq2uHDx1Im = Parameter(name = 'c8lq2uHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2uHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1008 ])

c8lq2uHDx2Re = Parameter(name = 'c8lq2uHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2uHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1009 ])

c8lq2uHDx2Im = Parameter(name = 'c8lq2uHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2uHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1010 ])

c8lq2uHDx3Re = Parameter(name = 'c8lq2uHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2uHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1011 ])

c8lq2uHDx3Im = Parameter(name = 'c8lq2uHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2uHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1012 ])

c8lq2dHDx1Re = Parameter(name = 'c8lq2dHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2dHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1013 ])

c8lq2dHDx1Im = Parameter(name = 'c8lq2dHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2dHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1014 ])

c8lq2dHDx2Re = Parameter(name = 'c8lq2dHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2dHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1015 ])

c8lq2dHDx2Im = Parameter(name = 'c8lq2dHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2dHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1016 ])

c8lq2dHDx3Re = Parameter(name = 'c8lq2dHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2dHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1017 ])

c8lq2dHDx3Im = Parameter(name = 'c8lq2dHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8lq2dHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1018 ])

c8eq3HDRe = Parameter(name = 'c8eq3HDRe',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8eq3HDRe}',
                      lhablock = 'DIM8',
                      lhacode = [ 1019 ])

c8eq3HDIm = Parameter(name = 'c8eq3HDIm',
                      nature = 'external',
                      type = 'real',
                      value = 0,
                      texname = '\\text{c8eq3HDIm}',
                      lhablock = 'DIM8',
                      lhacode = [ 1020 ])

c8equ2HDx1Re = Parameter(name = 'c8equ2HDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equ2HDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1021 ])

c8equ2HDx1Im = Parameter(name = 'c8equ2HDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equ2HDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1022 ])

c8equ2HDx2Re = Parameter(name = 'c8equ2HDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equ2HDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1023 ])

c8equ2HDx2Im = Parameter(name = 'c8equ2HDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equ2HDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1024 ])

c8equdHDx1Re = Parameter(name = 'c8equdHDx1Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equdHDx1Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1025 ])

c8equdHDx1Im = Parameter(name = 'c8equdHDx1Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equdHDx1Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1026 ])

c8equdHDx2Re = Parameter(name = 'c8equdHDx2Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equdHDx2Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1027 ])

c8equdHDx2Im = Parameter(name = 'c8equdHDx2Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equdHDx2Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1028 ])

c8equdHDx3Re = Parameter(name = 'c8equdHDx3Re',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equdHDx3Re}',
                         lhablock = 'DIM8',
                         lhacode = [ 1029 ])

c8equdHDx3Im = Parameter(name = 'c8equdHDx3Im',
                         nature = 'external',
                         type = 'real',
                         value = 0,
                         texname = '\\text{c8equdHDx3Im}',
                         lhablock = 'DIM8',
                         lhacode = [ 1030 ])

aEWM1 = Parameter(name = 'aEWM1',
                  nature = 'external',
                  type = 'real',
                  value = 127.9,
                  texname = '\\text{aEWM1}',
                  lhablock = 'SMINPUTS',
                  lhacode = [ 1 ])

Gf = Parameter(name = 'Gf',
               nature = 'external',
               type = 'real',
               value = 0.0000116637,
               texname = 'G_f',
               lhablock = 'SMINPUTS',
               lhacode = [ 2 ])

aS = Parameter(name = 'aS',
               nature = 'external',
               type = 'real',
               value = 0.1184,
               texname = '\\alpha _s',
               lhablock = 'SMINPUTS',
               lhacode = [ 3 ])

ymdo = Parameter(name = 'ymdo',
                 nature = 'external',
                 type = 'real',
                 value = 0.00504,
                 texname = '\\text{ymdo}',
                 lhablock = 'YUKAWA',
                 lhacode = [ 1 ])

ymup = Parameter(name = 'ymup',
                 nature = 'external',
                 type = 'real',
                 value = 0.00255,
                 texname = '\\text{ymup}',
                 lhablock = 'YUKAWA',
                 lhacode = [ 2 ])

yms = Parameter(name = 'yms',
                nature = 'external',
                type = 'real',
                value = 0.101,
                texname = '\\text{yms}',
                lhablock = 'YUKAWA',
                lhacode = [ 3 ])

ymc = Parameter(name = 'ymc',
                nature = 'external',
                type = 'real',
                value = 1.27,
                texname = '\\text{ymc}',
                lhablock = 'YUKAWA',
                lhacode = [ 4 ])

ymb = Parameter(name = 'ymb',
                nature = 'external',
                type = 'real',
                value = 4.7,
                texname = '\\text{ymb}',
                lhablock = 'YUKAWA',
                lhacode = [ 5 ])

ymt = Parameter(name = 'ymt',
                nature = 'external',
                type = 'real',
                value = 172,
                texname = '\\text{ymt}',
                lhablock = 'YUKAWA',
                lhacode = [ 6 ])

yme = Parameter(name = 'yme',
                nature = 'external',
                type = 'real',
                value = 0.000511,
                texname = '\\text{yme}',
                lhablock = 'YUKAWA',
                lhacode = [ 11 ])

ymm = Parameter(name = 'ymm',
                nature = 'external',
                type = 'real',
                value = 0.10566,
                texname = '\\text{ymm}',
                lhablock = 'YUKAWA',
                lhacode = [ 13 ])

ymtau = Parameter(name = 'ymtau',
                  nature = 'external',
                  type = 'real',
                  value = 1.777,
                  texname = '\\text{ymtau}',
                  lhablock = 'YUKAWA',
                  lhacode = [ 15 ])

MZ = Parameter(name = 'MZ',
               nature = 'external',
               type = 'real',
               value = 91.1876,
               texname = '\\text{MZ}',
               lhablock = 'MASS',
               lhacode = [ 23 ])

Me = Parameter(name = 'Me',
               nature = 'external',
               type = 'real',
               value = 0.000511,
               texname = '\\text{Me}',
               lhablock = 'MASS',
               lhacode = [ 11 ])

MMU = Parameter(name = 'MMU',
                nature = 'external',
                type = 'real',
                value = 0.10566,
                texname = '\\text{MMU}',
                lhablock = 'MASS',
                lhacode = [ 13 ])

MTA = Parameter(name = 'MTA',
                nature = 'external',
                type = 'real',
                value = 1.777,
                texname = '\\text{MTA}',
                lhablock = 'MASS',
                lhacode = [ 15 ])

MU = Parameter(name = 'MU',
               nature = 'external',
               type = 'real',
               value = 0.00255,
               texname = 'M',
               lhablock = 'MASS',
               lhacode = [ 2 ])

MC = Parameter(name = 'MC',
               nature = 'external',
               type = 'real',
               value = 1.27,
               texname = '\\text{MC}',
               lhablock = 'MASS',
               lhacode = [ 4 ])

MT = Parameter(name = 'MT',
               nature = 'external',
               type = 'real',
               value = 172,
               texname = '\\text{MT}',
               lhablock = 'MASS',
               lhacode = [ 6 ])

MD = Parameter(name = 'MD',
               nature = 'external',
               type = 'real',
               value = 0.00504,
               texname = '\\text{MD}',
               lhablock = 'MASS',
               lhacode = [ 1 ])

MS = Parameter(name = 'MS',
               nature = 'external',
               type = 'real',
               value = 0.101,
               texname = '\\text{MS}',
               lhablock = 'MASS',
               lhacode = [ 3 ])

MB = Parameter(name = 'MB',
               nature = 'external',
               type = 'real',
               value = 4.7,
               texname = '\\text{MB}',
               lhablock = 'MASS',
               lhacode = [ 5 ])

MH = Parameter(name = 'MH',
               nature = 'external',
               type = 'real',
               value = 125,
               texname = '\\text{MH}',
               lhablock = 'MASS',
               lhacode = [ 25 ])

WZ = Parameter(name = 'WZ',
               nature = 'external',
               type = 'real',
               value = 2.4952,
               texname = '\\text{WZ}',
               lhablock = 'DECAY',
               lhacode = [ 23 ])

WW = Parameter(name = 'WW',
               nature = 'external',
               type = 'real',
               value = 2.085,
               texname = '\\text{WW}',
               lhablock = 'DECAY',
               lhacode = [ 24 ])

WT = Parameter(name = 'WT',
               nature = 'external',
               type = 'real',
               value = 1.50833649,
               texname = '\\text{WT}',
               lhablock = 'DECAY',
               lhacode = [ 6 ])

WH = Parameter(name = 'WH',
               nature = 'external',
               type = 'real',
               value = 0.00407,
               texname = '\\text{WH}',
               lhablock = 'DECAY',
               lhacode = [ 25 ])

aEW = Parameter(name = 'aEW',
                nature = 'internal',
                type = 'real',
                value = '1/aEWM1',
                texname = '\\alpha _{\\text{EW}}')

L6 = Parameter(name = 'L6',
               nature = 'internal',
               type = 'real',
               value = 'Lam6**(-2)',
               texname = '\\text{L6}')

L8 = Parameter(name = 'L8',
               nature = 'internal',
               type = 'real',
               value = 'Lam**(-4)',
               texname = '\\text{L8}')

vevSM = Parameter(name = 'vevSM',
                  nature = 'internal',
                  type = 'real',
                  value = '1/(2**0.25*cmath.sqrt(Gf))',
                  texname = '\\text{vevSM}')

G = Parameter(name = 'G',
              nature = 'internal',
              type = 'real',
              value = '2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)',
              texname = 'G')

CKM1x1 = Parameter(name = 'CKM1x1',
                   nature = 'internal',
                   type = 'complex',
                   value = 'cmath.cos(cabi)',
                   texname = '\\text{CKM1x1}')

CKM1x2 = Parameter(name = 'CKM1x2',
                   nature = 'internal',
                   type = 'complex',
                   value = 'cmath.sin(cabi)',
                   texname = '\\text{CKM1x2}')

CKM1x3 = Parameter(name = 'CKM1x3',
                   nature = 'internal',
                   type = 'complex',
                   value = '0',
                   texname = '\\text{CKM1x3}')

CKM2x1 = Parameter(name = 'CKM2x1',
                   nature = 'internal',
                   type = 'complex',
                   value = '-cmath.sin(cabi)',
                   texname = '\\text{CKM2x1}')

CKM2x2 = Parameter(name = 'CKM2x2',
                   nature = 'internal',
                   type = 'complex',
                   value = 'cmath.cos(cabi)',
                   texname = '\\text{CKM2x2}')

CKM2x3 = Parameter(name = 'CKM2x3',
                   nature = 'internal',
                   type = 'complex',
                   value = '0',
                   texname = '\\text{CKM2x3}')

CKM3x1 = Parameter(name = 'CKM3x1',
                   nature = 'internal',
                   type = 'complex',
                   value = '0',
                   texname = '\\text{CKM3x1}')

CKM3x2 = Parameter(name = 'CKM3x2',
                   nature = 'internal',
                   type = 'complex',
                   value = '0',
                   texname = '\\text{CKM3x2}')

CKM3x3 = Parameter(name = 'CKM3x3',
                   nature = 'internal',
                   type = 'complex',
                   value = '1',
                   texname = '\\text{CKM3x3}')

epsLorSign = Parameter(name = 'epsLorSign',
                       nature = 'internal',
                       type = 'real',
                       value = '1',
                       texname = '\\text{epsLorSign}')

c8leWH3x1 = Parameter(name = 'c8leWH3x1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leWH3x1Re + c8leWH3x1Im*complex(0,1)',
                      texname = '\\text{c8leWH3x1}')

c8leWH3x2 = Parameter(name = 'c8leWH3x2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leWH3x2Re + c8leWH3x2Im*complex(0,1)',
                      texname = '\\text{c8leWH3x2}')

c8leBH3 = Parameter(name = 'c8leBH3',
                    nature = 'internal',
                    type = 'complex',
                    value = 'c8leBH3Re + c8leBH3Im*complex(0,1)',
                    texname = '\\text{c8leBH3}')

c8quGH3 = Parameter(name = 'c8quGH3',
                    nature = 'internal',
                    type = 'complex',
                    value = 'c8quGH3Re + c8quGH3Im*complex(0,1)',
                    texname = '\\text{c8quGH3}')

c8quWH3x1 = Parameter(name = 'c8quWH3x1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quWH3x1Re + c8quWH3x1Im*complex(0,1)',
                      texname = '\\text{c8quWH3x1}')

c8quWH3x2 = Parameter(name = 'c8quWH3x2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quWH3x2Re + c8quWH3x2Im*complex(0,1)',
                      texname = '\\text{c8quWH3x2}')

c8quBH3 = Parameter(name = 'c8quBH3',
                    nature = 'internal',
                    type = 'complex',
                    value = 'c8quBH3Re + c8quBH3Im*complex(0,1)',
                    texname = '\\text{c8quBH3}')

c8qdGH3 = Parameter(name = 'c8qdGH3',
                    nature = 'internal',
                    type = 'complex',
                    value = 'c8qdGH3Re + c8qdGH3Im*complex(0,1)',
                    texname = '\\text{c8qdGH3}')

c8qdWH3x1 = Parameter(name = 'c8qdWH3x1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdWH3x1Re + c8qdWH3x1Im*complex(0,1)',
                      texname = '\\text{c8qdWH3x1}')

c8qdWH3x2 = Parameter(name = 'c8qdWH3x2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdWH3x2Re + c8qdWH3x2Im*complex(0,1)',
                      texname = '\\text{c8qdWH3x2}')

c8qdBH3 = Parameter(name = 'c8qdBH3',
                    nature = 'internal',
                    type = 'complex',
                    value = 'c8qdBH3Re + c8qdBH3Im*complex(0,1)',
                    texname = '\\text{c8qdBH3}')

c8udH2D3 = Parameter(name = 'c8udH2D3',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8udH2D3Re + c8udH2D3Im*complex(0,1)',
                     texname = '\\text{c8udH2D3}')

c8leH5 = Parameter(name = 'c8leH5',
                   nature = 'internal',
                   type = 'complex',
                   value = 'c8leH5Re + c8leH5Im*complex(0,1)',
                   texname = '\\text{c8leH5}')

c8quH5 = Parameter(name = 'c8quH5',
                   nature = 'internal',
                   type = 'complex',
                   value = 'c8quH5Re + c8quH5Im*complex(0,1)',
                   texname = '\\text{c8quH5}')

c8qdH5 = Parameter(name = 'c8qdH5',
                   nature = 'internal',
                   type = 'complex',
                   value = 'c8qdH5Re + c8qdH5Im*complex(0,1)',
                   texname = '\\text{c8qdH5}')

c8udH4D = Parameter(name = 'c8udH4D',
                    nature = 'internal',
                    type = 'complex',
                    value = 'c8udH4DRe + c8udH4DIm*complex(0,1)',
                    texname = '\\text{c8udH4D}')

c8udGH2x1 = Parameter(name = 'c8udGH2x1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8udGH2x1Re + c8udGH2x1Im*complex(0,1)',
                      texname = '\\text{c8udGH2x1}')

c8udGH2x2 = Parameter(name = 'c8udGH2x2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8udGH2x2Re + c8udGH2x2Im*complex(0,1)',
                      texname = '\\text{c8udGH2x2}')

c8udWH2x1 = Parameter(name = 'c8udWH2x1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8udWH2x1Re + c8udWH2x1Im*complex(0,1)',
                      texname = '\\text{c8udWH2x1}')

c8udWH2x2 = Parameter(name = 'c8udWH2x2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8udWH2x2Re + c8udWH2x2Im*complex(0,1)',
                      texname = '\\text{c8udWH2x2}')

c8udBH2x1 = Parameter(name = 'c8udBH2x1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8udBH2x1Re + c8udBH2x1Im*complex(0,1)',
                      texname = '\\text{c8udBH2x1}')

c8udBH2x2 = Parameter(name = 'c8udBH2x2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8udBH2x2Re + c8udBH2x2Im*complex(0,1)',
                      texname = '\\text{c8udBH2x2}')

c8leWHD2x1 = Parameter(name = 'c8leWHD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leWHD2x1Re + c8leWHD2x1Im*complex(0,1)',
                       texname = '\\text{c8leWHD2x1}')

c8leWHD2x2 = Parameter(name = 'c8leWHD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leWHD2x2Re + c8leWHD2x2Im*complex(0,1)',
                       texname = '\\text{c8leWHD2x2}')

c8leWHD2x3 = Parameter(name = 'c8leWHD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leWHD2x3Re + c8leWHD2x3Im*complex(0,1)',
                       texname = '\\text{c8leWHD2x3}')

c8leBHD2x1 = Parameter(name = 'c8leBHD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leBHD2x1Re + c8leBHD2x1Im*complex(0,1)',
                       texname = '\\text{c8leBHD2x1}')

c8leBHD2x2 = Parameter(name = 'c8leBHD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leBHD2x2Re + c8leBHD2x2Im*complex(0,1)',
                       texname = '\\text{c8leBHD2x2}')

c8leBHD2x3 = Parameter(name = 'c8leBHD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leBHD2x3Re + c8leBHD2x3Im*complex(0,1)',
                       texname = '\\text{c8leBHD2x3}')

c8quGHD2x1 = Parameter(name = 'c8quGHD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quGHD2x1Re + c8quGHD2x1Im*complex(0,1)',
                       texname = '\\text{c8quGHD2x1}')

c8quGHD2x2 = Parameter(name = 'c8quGHD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quGHD2x2Re + c8quGHD2x2Im*complex(0,1)',
                       texname = '\\text{c8quGHD2x2}')

c8quGHD2x3 = Parameter(name = 'c8quGHD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quGHD2x3Re + c8quGHD2x3Im*complex(0,1)',
                       texname = '\\text{c8quGHD2x3}')

c8quWHD2x1 = Parameter(name = 'c8quWHD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quWHD2x1Re + c8quWHD2x1Im*complex(0,1)',
                       texname = '\\text{c8quWHD2x1}')

c8quWHD2x2 = Parameter(name = 'c8quWHD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quWHD2x2Re + c8quWHD2x2Im*complex(0,1)',
                       texname = '\\text{c8quWHD2x2}')

c8quWHD2x3 = Parameter(name = 'c8quWHD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quWHD2x3Re + c8quWHD2x3Im*complex(0,1)',
                       texname = '\\text{c8quWHD2x3}')

c8quBHD2x1 = Parameter(name = 'c8quBHD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quBHD2x1Re + c8quBHD2x1Im*complex(0,1)',
                       texname = '\\text{c8quBHD2x1}')

c8quBHD2x2 = Parameter(name = 'c8quBHD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quBHD2x2Re + c8quBHD2x2Im*complex(0,1)',
                       texname = '\\text{c8quBHD2x2}')

c8quBHD2x3 = Parameter(name = 'c8quBHD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quBHD2x3Re + c8quBHD2x3Im*complex(0,1)',
                       texname = '\\text{c8quBHD2x3}')

c8qdGHD2x1 = Parameter(name = 'c8qdGHD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdGHD2x1Re + c8qdGHD2x1Im*complex(0,1)',
                       texname = '\\text{c8qdGHD2x1}')

c8qdGHD2x2 = Parameter(name = 'c8qdGHD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdGHD2x2Re + c8qdGHD2x2Im*complex(0,1)',
                       texname = '\\text{c8qdGHD2x2}')

c8qdGHD2x3 = Parameter(name = 'c8qdGHD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdGHD2x3Re + c8qdGHD2x3Im*complex(0,1)',
                       texname = '\\text{c8qdGHD2x3}')

c8qdWHD2x1 = Parameter(name = 'c8qdWHD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdWHD2x1Re + c8qdWHD2x1Im*complex(0,1)',
                       texname = '\\text{c8qdWHD2x1}')

c8qdWHD2x2 = Parameter(name = 'c8qdWHD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdWHD2x2Re + c8qdWHD2x2Im*complex(0,1)',
                       texname = '\\text{c8qdWHD2x2}')

c8qdWHD2x3 = Parameter(name = 'c8qdWHD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdWHD2x3Re + c8qdWHD2x3Im*complex(0,1)',
                       texname = '\\text{c8qdWHD2x3}')

c8qdBHD2x1 = Parameter(name = 'c8qdBHD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdBHD2x1Re + c8qdBHD2x1Im*complex(0,1)',
                       texname = '\\text{c8qdBHD2x1}')

c8qdBHD2x2 = Parameter(name = 'c8qdBHD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdBHD2x2Re + c8qdBHD2x2Im*complex(0,1)',
                       texname = '\\text{c8qdBHD2x2}')

c8qdBHD2x3 = Parameter(name = 'c8qdBHD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdBHD2x3Re + c8qdBHD2x3Im*complex(0,1)',
                       texname = '\\text{c8qdBHD2x3}')

c8leH3D2x1 = Parameter(name = 'c8leH3D2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leH3D2x1Re + c8leH3D2x1Im*complex(0,1)',
                       texname = '\\text{c8leH3D2x1}')

c8leH3D2x2 = Parameter(name = 'c8leH3D2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leH3D2x2Re + c8leH3D2x2Im*complex(0,1)',
                       texname = '\\text{c8leH3D2x2}')

c8leH3D2x3 = Parameter(name = 'c8leH3D2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leH3D2x3Re + c8leH3D2x3Im*complex(0,1)',
                       texname = '\\text{c8leH3D2x3}')

c8leH3D2x4 = Parameter(name = 'c8leH3D2x4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leH3D2x4Re + c8leH3D2x4Im*complex(0,1)',
                       texname = '\\text{c8leH3D2x4}')

c8leH3D2x5 = Parameter(name = 'c8leH3D2x5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leH3D2x5Re + c8leH3D2x5Im*complex(0,1)',
                       texname = '\\text{c8leH3D2x5}')

c8leH3D2x6 = Parameter(name = 'c8leH3D2x6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leH3D2x6Re + c8leH3D2x6Im*complex(0,1)',
                       texname = '\\text{c8leH3D2x6}')

c8quH3D2x1 = Parameter(name = 'c8quH3D2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quH3D2x1Re + c8quH3D2x1Im*complex(0,1)',
                       texname = '\\text{c8quH3D2x1}')

c8quH3D2x2 = Parameter(name = 'c8quH3D2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quH3D2x2Re + c8quH3D2x2Im*complex(0,1)',
                       texname = '\\text{c8quH3D2x2}')

c8quH3D2x3 = Parameter(name = 'c8quH3D2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quH3D2x3Re + c8quH3D2x3Im*complex(0,1)',
                       texname = '\\text{c8quH3D2x3}')

c8quH3D2x4 = Parameter(name = 'c8quH3D2x4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quH3D2x4Re + c8quH3D2x4Im*complex(0,1)',
                       texname = '\\text{c8quH3D2x4}')

c8quH3D2x5 = Parameter(name = 'c8quH3D2x5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quH3D2x5Re + c8quH3D2x5Im*complex(0,1)',
                       texname = '\\text{c8quH3D2x5}')

c8quH3D2x6 = Parameter(name = 'c8quH3D2x6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8quH3D2x6Re + c8quH3D2x6Im*complex(0,1)',
                       texname = '\\text{c8quH3D2x6}')

c8qdH3D2x1 = Parameter(name = 'c8qdH3D2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdH3D2x1Re + c8qdH3D2x1Im*complex(0,1)',
                       texname = '\\text{c8qdH3D2x1}')

c8qdH3D2x2 = Parameter(name = 'c8qdH3D2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdH3D2x2Re + c8qdH3D2x2Im*complex(0,1)',
                       texname = '\\text{c8qdH3D2x2}')

c8qdH3D2x3 = Parameter(name = 'c8qdH3D2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdH3D2x3Re + c8qdH3D2x3Im*complex(0,1)',
                       texname = '\\text{c8qdH3D2x3}')

c8qdH3D2x4 = Parameter(name = 'c8qdH3D2x4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdH3D2x4Re + c8qdH3D2x4Im*complex(0,1)',
                       texname = '\\text{c8qdH3D2x4}')

c8qdH3D2x5 = Parameter(name = 'c8qdH3D2x5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdH3D2x5Re + c8qdH3D2x5Im*complex(0,1)',
                       texname = '\\text{c8qdH3D2x5}')

c8qdH3D2x6 = Parameter(name = 'c8qdH3D2x6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qdH3D2x6Re + c8qdH3D2x6Im*complex(0,1)',
                       texname = '\\text{c8qdH3D2x6}')

c8leqdH2x1 = Parameter(name = 'c8leqdH2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leqdH2x1Re + c8leqdH2x1Im*complex(0,1)',
                       texname = '\\text{c8leqdH2x1}')

c8leqdH2x2 = Parameter(name = 'c8leqdH2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leqdH2x2Re + c8leqdH2x2Im*complex(0,1)',
                       texname = '\\text{c8leqdH2x2}')

c8l2udH2 = Parameter(name = 'c8l2udH2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8l2udH2Re + c8l2udH2Im*complex(0,1)',
                     texname = '\\text{c8l2udH2}')

c8lequH2x5 = Parameter(name = 'c8lequH2x5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lequH2x5Re + c8lequH2x5Im*complex(0,1)',
                       texname = '\\text{c8lequH2x5}')

c8q2udH2x5 = Parameter(name = 'c8q2udH2x5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udH2x5Re + c8q2udH2x5Im*complex(0,1)',
                       texname = '\\text{c8q2udH2x5}')

c8q2udH2x6 = Parameter(name = 'c8q2udH2x6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udH2x6Re + c8q2udH2x6Im*complex(0,1)',
                       texname = '\\text{c8q2udH2x6}')

c8leqdD2x1 = Parameter(name = 'c8leqdD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leqdD2x1Re + c8leqdD2x1Im*complex(0,1)',
                       texname = '\\text{c8leqdD2x1}')

c8leqdD2x2 = Parameter(name = 'c8leqdD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leqdD2x2Re + c8leqdD2x2Im*complex(0,1)',
                       texname = '\\text{c8leqdD2x2}')

c8q2udH2x1 = Parameter(name = 'c8q2udH2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udH2x1Re + c8q2udH2x1Im*complex(0,1)',
                       texname = '\\text{c8q2udH2x1}')

c8q2udH2x2 = Parameter(name = 'c8q2udH2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udH2x2Re + c8q2udH2x2Im*complex(0,1)',
                       texname = '\\text{c8q2udH2x2}')

c8q2udH2x3 = Parameter(name = 'c8q2udH2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udH2x3Re + c8q2udH2x3Im*complex(0,1)',
                       texname = '\\text{c8q2udH2x3}')

c8q2udH2x4 = Parameter(name = 'c8q2udH2x4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udH2x4Re + c8q2udH2x4Im*complex(0,1)',
                       texname = '\\text{c8q2udH2x4}')

c8lequH2x1 = Parameter(name = 'c8lequH2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lequH2x1Re + c8lequH2x1Im*complex(0,1)',
                       texname = '\\text{c8lequH2x1}')

c8lequH2x2 = Parameter(name = 'c8lequH2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lequH2x2Re + c8lequH2x2Im*complex(0,1)',
                       texname = '\\text{c8lequH2x2}')

c8lequH2x3 = Parameter(name = 'c8lequH2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lequH2x3Re + c8lequH2x3Im*complex(0,1)',
                       texname = '\\text{c8lequH2x3}')

c8lequH2x4 = Parameter(name = 'c8lequH2x4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lequH2x4Re + c8lequH2x4Im*complex(0,1)',
                       texname = '\\text{c8lequH2x4}')

c8l2e2H2x3 = Parameter(name = 'c8l2e2H2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2e2H2x3Re + c8l2e2H2x3Im*complex(0,1)',
                       texname = '\\text{c8l2e2H2x3}')

c8leqdH2x3 = Parameter(name = 'c8leqdH2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leqdH2x3Re + c8leqdH2x3Im*complex(0,1)',
                       texname = '\\text{c8leqdH2x3}')

c8leqdH2x4 = Parameter(name = 'c8leqdH2x4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leqdH2x4Re + c8leqdH2x4Im*complex(0,1)',
                       texname = '\\text{c8leqdH2x4}')

c8q2u2H2x5 = Parameter(name = 'c8q2u2H2x5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2u2H2x5Re + c8q2u2H2x5Im*complex(0,1)',
                       texname = '\\text{c8q2u2H2x5}')

c8q2u2H2x6 = Parameter(name = 'c8q2u2H2x6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2u2H2x6Re + c8q2u2H2x6Im*complex(0,1)',
                       texname = '\\text{c8q2u2H2x6}')

c8q2d2H2x5 = Parameter(name = 'c8q2d2H2x5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2d2H2x5Re + c8q2d2H2x5Im*complex(0,1)',
                       texname = '\\text{c8q2d2H2x5}')

c8q2d2H2x6 = Parameter(name = 'c8q2d2H2x6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2d2H2x6Re + c8q2d2H2x6Im*complex(0,1)',
                       texname = '\\text{c8q2d2H2x6}')

c8ledqGx1 = Parameter(name = 'c8ledqGx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8ledqGx1Re + c8ledqGx1Im*complex(0,1)',
                      texname = '\\text{c8ledqGx1}')

c8ledqGx2 = Parameter(name = 'c8ledqGx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8ledqGx2Re + c8ledqGx2Im*complex(0,1)',
                      texname = '\\text{c8ledqGx2}')

c8ledqWx1 = Parameter(name = 'c8ledqWx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8ledqWx1Re + c8ledqWx1Im*complex(0,1)',
                      texname = '\\text{c8ledqWx1}')

c8ledqWx2 = Parameter(name = 'c8ledqWx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8ledqWx2Re + c8ledqWx2Im*complex(0,1)',
                      texname = '\\text{c8ledqWx2}')

c8ledqBx1 = Parameter(name = 'c8ledqBx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8ledqBx1Re + c8ledqBx1Im*complex(0,1)',
                      texname = '\\text{c8ledqBx1}')

c8ledqBx2 = Parameter(name = 'c8ledqBx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8ledqBx2Re + c8ledqBx2Im*complex(0,1)',
                      texname = '\\text{c8ledqBx2}')

c8q2udGx1 = Parameter(name = 'c8q2udGx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udGx1Re + c8q2udGx1Im*complex(0,1)',
                      texname = '\\text{c8q2udGx1}')

c8q2udGx2 = Parameter(name = 'c8q2udGx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udGx2Re + c8q2udGx2Im*complex(0,1)',
                      texname = '\\text{c8q2udGx2}')

c8q2udGx3 = Parameter(name = 'c8q2udGx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udGx3Re + c8q2udGx3Im*complex(0,1)',
                      texname = '\\text{c8q2udGx3}')

c8q2udGx4 = Parameter(name = 'c8q2udGx4',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udGx4Re + c8q2udGx4Im*complex(0,1)',
                      texname = '\\text{c8q2udGx4}')

c8q2udGx5 = Parameter(name = 'c8q2udGx5',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udGx5Re + c8q2udGx5Im*complex(0,1)',
                      texname = '\\text{c8q2udGx5}')

c8q2udGx6 = Parameter(name = 'c8q2udGx6',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udGx6Re + c8q2udGx6Im*complex(0,1)',
                      texname = '\\text{c8q2udGx6}')

c8q2udWx1 = Parameter(name = 'c8q2udWx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udWx1Re + c8q2udWx1Im*complex(0,1)',
                      texname = '\\text{c8q2udWx1}')

c8q2udWx2 = Parameter(name = 'c8q2udWx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udWx2Re + c8q2udWx2Im*complex(0,1)',
                      texname = '\\text{c8q2udWx2}')

c8q2udWx3 = Parameter(name = 'c8q2udWx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udWx3Re + c8q2udWx3Im*complex(0,1)',
                      texname = '\\text{c8q2udWx3}')

c8q2udBx1 = Parameter(name = 'c8q2udBx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udBx1Re + c8q2udBx1Im*complex(0,1)',
                      texname = '\\text{c8q2udBx1}')

c8q2udBx2 = Parameter(name = 'c8q2udBx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udBx2Re + c8q2udBx2Im*complex(0,1)',
                      texname = '\\text{c8q2udBx2}')

c8q2udBx3 = Parameter(name = 'c8q2udBx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q2udBx3Re + c8q2udBx3Im*complex(0,1)',
                      texname = '\\text{c8q2udBx3}')

c8lequGx1 = Parameter(name = 'c8lequGx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequGx1Re + c8lequGx1Im*complex(0,1)',
                      texname = '\\text{c8lequGx1}')

c8lequGx2 = Parameter(name = 'c8lequGx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequGx2Re + c8lequGx2Im*complex(0,1)',
                      texname = '\\text{c8lequGx2}')

c8lequGx3 = Parameter(name = 'c8lequGx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequGx3Re + c8lequGx3Im*complex(0,1)',
                      texname = '\\text{c8lequGx3}')

c8lequWx1 = Parameter(name = 'c8lequWx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequWx1Re + c8lequWx1Im*complex(0,1)',
                      texname = '\\text{c8lequWx1}')

c8lequWx2 = Parameter(name = 'c8lequWx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequWx2Re + c8lequWx2Im*complex(0,1)',
                      texname = '\\text{c8lequWx2}')

c8lequWx3 = Parameter(name = 'c8lequWx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequWx3Re + c8lequWx3Im*complex(0,1)',
                      texname = '\\text{c8lequWx3}')

c8lequBx1 = Parameter(name = 'c8lequBx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequBx1Re + c8lequBx1Im*complex(0,1)',
                      texname = '\\text{c8lequBx1}')

c8lequBx2 = Parameter(name = 'c8lequBx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequBx2Re + c8lequBx2Im*complex(0,1)',
                      texname = '\\text{c8lequBx2}')

c8lequBx3 = Parameter(name = 'c8lequBx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lequBx3Re + c8lequBx3Im*complex(0,1)',
                      texname = '\\text{c8lequBx3}')

c8l3eHDx1 = Parameter(name = 'c8l3eHDx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8l3eHDx1Re + c8l3eHDx1Im*complex(0,1)',
                      texname = '\\text{c8l3eHDx1}')

c8l3eHDx2 = Parameter(name = 'c8l3eHDx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8l3eHDx2Re + c8l3eHDx2Im*complex(0,1)',
                      texname = '\\text{c8l3eHDx2}')

c8l3eHDx3 = Parameter(name = 'c8l3eHDx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8l3eHDx3Re + c8l3eHDx3Im*complex(0,1)',
                      texname = '\\text{c8l3eHDx3}')

c8le3HDx1 = Parameter(name = 'c8le3HDx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8le3HDx1Re + c8le3HDx1Im*complex(0,1)',
                      texname = '\\text{c8le3HDx1}')

c8leq2HDx1 = Parameter(name = 'c8leq2HDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leq2HDx1Re + c8leq2HDx1Im*complex(0,1)',
                       texname = '\\text{c8leq2HDx1}')

c8leq2HDx2 = Parameter(name = 'c8leq2HDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leq2HDx2Re + c8leq2HDx2Im*complex(0,1)',
                       texname = '\\text{c8leq2HDx2}')

c8leq2HDx3 = Parameter(name = 'c8leq2HDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leq2HDx3Re + c8leq2HDx3Im*complex(0,1)',
                       texname = '\\text{c8leq2HDx3}')

c8leq2HDx4 = Parameter(name = 'c8leq2HDx4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leq2HDx4Re + c8leq2HDx4Im*complex(0,1)',
                       texname = '\\text{c8leq2HDx4}')

c8leq2HDx5 = Parameter(name = 'c8leq2HDx5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leq2HDx5Re + c8leq2HDx5Im*complex(0,1)',
                       texname = '\\text{c8leq2HDx5}')

c8leq2HDx6 = Parameter(name = 'c8leq2HDx6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leq2HDx6Re + c8leq2HDx6Im*complex(0,1)',
                       texname = '\\text{c8leq2HDx6}')

c8leu2HDx1 = Parameter(name = 'c8leu2HDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leu2HDx1Re + c8leu2HDx1Im*complex(0,1)',
                       texname = '\\text{c8leu2HDx1}')

c8leu2HDx2 = Parameter(name = 'c8leu2HDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leu2HDx2Re + c8leu2HDx2Im*complex(0,1)',
                       texname = '\\text{c8leu2HDx2}')

c8leu2HDx3 = Parameter(name = 'c8leu2HDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leu2HDx3Re + c8leu2HDx3Im*complex(0,1)',
                       texname = '\\text{c8leu2HDx3}')

c8led2HDx1 = Parameter(name = 'c8led2HDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8led2HDx1Re + c8led2HDx1Im*complex(0,1)',
                       texname = '\\text{c8led2HDx1}')

c8led2HDx2 = Parameter(name = 'c8led2HDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8led2HDx2Re + c8led2HDx2Im*complex(0,1)',
                       texname = '\\text{c8led2HDx2}')

c8led2HDx3 = Parameter(name = 'c8led2HDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8led2HDx3Re + c8led2HDx3Im*complex(0,1)',
                       texname = '\\text{c8led2HDx3}')

c8leudHDx1 = Parameter(name = 'c8leudHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leudHDx1Re + c8leudHDx1Im*complex(0,1)',
                       texname = '\\text{c8leudHDx1}')

c8leudHDx2 = Parameter(name = 'c8leudHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leudHDx2Re + c8leudHDx2Im*complex(0,1)',
                       texname = '\\text{c8leudHDx2}')

c8leudHDx3 = Parameter(name = 'c8leudHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8leudHDx3Re + c8leudHDx3Im*complex(0,1)',
                       texname = '\\text{c8leudHDx3}')

c8le3HDx2 = Parameter(name = 'c8le3HDx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8le3HDx2Re + c8le3HDx2Im*complex(0,1)',
                      texname = '\\text{c8le3HDx2}')

c8l2quHDx1 = Parameter(name = 'c8l2quHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2quHDx1Re + c8l2quHDx1Im*complex(0,1)',
                       texname = '\\text{c8l2quHDx1}')

c8l2quHDx2 = Parameter(name = 'c8l2quHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2quHDx2Re + c8l2quHDx2Im*complex(0,1)',
                       texname = '\\text{c8l2quHDx2}')

c8l2quHDx3 = Parameter(name = 'c8l2quHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2quHDx3Re + c8l2quHDx3Im*complex(0,1)',
                       texname = '\\text{c8l2quHDx3}')

c8l2quHDx4 = Parameter(name = 'c8l2quHDx4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2quHDx4Re + c8l2quHDx4Im*complex(0,1)',
                       texname = '\\text{c8l2quHDx4}')

c8l2quHDx5 = Parameter(name = 'c8l2quHDx5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2quHDx5Re + c8l2quHDx5Im*complex(0,1)',
                       texname = '\\text{c8l2quHDx5}')

c8l2quHDx6 = Parameter(name = 'c8l2quHDx6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2quHDx6Re + c8l2quHDx6Im*complex(0,1)',
                       texname = '\\text{c8l2quHDx6}')

c8e2quHDx1 = Parameter(name = 'c8e2quHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8e2quHDx1Re + c8e2quHDx1Im*complex(0,1)',
                       texname = '\\text{c8e2quHDx1}')

c8e2quHDx2 = Parameter(name = 'c8e2quHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8e2quHDx2Re + c8e2quHDx2Im*complex(0,1)',
                       texname = '\\text{c8e2quHDx2}')

c8e2quHDx3 = Parameter(name = 'c8e2quHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8e2quHDx3Re + c8e2quHDx3Im*complex(0,1)',
                       texname = '\\text{c8e2quHDx3}')

c8q3uHDx1 = Parameter(name = 'c8q3uHDx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3uHDx1Re + c8q3uHDx1Im*complex(0,1)',
                      texname = '\\text{c8q3uHDx1}')

c8q3uHDx2 = Parameter(name = 'c8q3uHDx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3uHDx2Re + c8q3uHDx2Im*complex(0,1)',
                      texname = '\\text{c8q3uHDx2}')

c8q3uHDx3 = Parameter(name = 'c8q3uHDx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3uHDx3Re + c8q3uHDx3Im*complex(0,1)',
                      texname = '\\text{c8q3uHDx3}')

c8q3uHDx4 = Parameter(name = 'c8q3uHDx4',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3uHDx4Re + c8q3uHDx4Im*complex(0,1)',
                      texname = '\\text{c8q3uHDx4}')

c8q3uHDx5 = Parameter(name = 'c8q3uHDx5',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3uHDx5Re + c8q3uHDx5Im*complex(0,1)',
                      texname = '\\text{c8q3uHDx5}')

c8q3uHDx6 = Parameter(name = 'c8q3uHDx6',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3uHDx6Re + c8q3uHDx6Im*complex(0,1)',
                      texname = '\\text{c8q3uHDx6}')

c8qu3HDx1 = Parameter(name = 'c8qu3HDx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qu3HDx1Re + c8qu3HDx1Im*complex(0,1)',
                      texname = '\\text{c8qu3HDx1}')

c8qu3HDx2 = Parameter(name = 'c8qu3HDx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qu3HDx2Re + c8qu3HDx2Im*complex(0,1)',
                      texname = '\\text{c8qu3HDx2}')

c8qu3HDx3 = Parameter(name = 'c8qu3HDx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qu3HDx3Re + c8qu3HDx3Im*complex(0,1)',
                      texname = '\\text{c8qu3HDx3}')

c8qud2HDx1 = Parameter(name = 'c8qud2HDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qud2HDx1Re + c8qud2HDx1Im*complex(0,1)',
                       texname = '\\text{c8qud2HDx1}')

c8qud2HDx2 = Parameter(name = 'c8qud2HDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qud2HDx2Re + c8qud2HDx2Im*complex(0,1)',
                       texname = '\\text{c8qud2HDx2}')

c8qud2HDx3 = Parameter(name = 'c8qud2HDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qud2HDx3Re + c8qud2HDx3Im*complex(0,1)',
                       texname = '\\text{c8qud2HDx3}')

c8qud2HDx4 = Parameter(name = 'c8qud2HDx4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qud2HDx4Re + c8qud2HDx4Im*complex(0,1)',
                       texname = '\\text{c8qud2HDx4}')

c8qud2HDx5 = Parameter(name = 'c8qud2HDx5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qud2HDx5Re + c8qud2HDx5Im*complex(0,1)',
                       texname = '\\text{c8qud2HDx5}')

c8qud2HDx6 = Parameter(name = 'c8qud2HDx6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qud2HDx6Re + c8qud2HDx6Im*complex(0,1)',
                       texname = '\\text{c8qud2HDx6}')

c8l2qdHDx1 = Parameter(name = 'c8l2qdHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2qdHDx1Re + c8l2qdHDx1Im*complex(0,1)',
                       texname = '\\text{c8l2qdHDx1}')

c8l2qdHDx2 = Parameter(name = 'c8l2qdHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2qdHDx2Re + c8l2qdHDx2Im*complex(0,1)',
                       texname = '\\text{c8l2qdHDx2}')

c8l2qdHDx3 = Parameter(name = 'c8l2qdHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2qdHDx3Re + c8l2qdHDx3Im*complex(0,1)',
                       texname = '\\text{c8l2qdHDx3}')

c8l2qdHDx4 = Parameter(name = 'c8l2qdHDx4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2qdHDx4Re + c8l2qdHDx4Im*complex(0,1)',
                       texname = '\\text{c8l2qdHDx4}')

c8l2qdHDx5 = Parameter(name = 'c8l2qdHDx5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2qdHDx5Re + c8l2qdHDx5Im*complex(0,1)',
                       texname = '\\text{c8l2qdHDx5}')

c8l2qdHDx6 = Parameter(name = 'c8l2qdHDx6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8l2qdHDx6Re + c8l2qdHDx6Im*complex(0,1)',
                       texname = '\\text{c8l2qdHDx6}')

c8e2qdHDx1 = Parameter(name = 'c8e2qdHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8e2qdHDx1Re + c8e2qdHDx1Im*complex(0,1)',
                       texname = '\\text{c8e2qdHDx1}')

c8e2qdHDx2 = Parameter(name = 'c8e2qdHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8e2qdHDx2Re + c8e2qdHDx2Im*complex(0,1)',
                       texname = '\\text{c8e2qdHDx2}')

c8e2qdHDx3 = Parameter(name = 'c8e2qdHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8e2qdHDx3Re + c8e2qdHDx3Im*complex(0,1)',
                       texname = '\\text{c8e2qdHDx3}')

c8q3dHDx1 = Parameter(name = 'c8q3dHDx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3dHDx1Re + c8q3dHDx1Im*complex(0,1)',
                      texname = '\\text{c8q3dHDx1}')

c8q3dHDx2 = Parameter(name = 'c8q3dHDx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3dHDx2Re + c8q3dHDx2Im*complex(0,1)',
                      texname = '\\text{c8q3dHDx2}')

c8q3dHDx3 = Parameter(name = 'c8q3dHDx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3dHDx3Re + c8q3dHDx3Im*complex(0,1)',
                      texname = '\\text{c8q3dHDx3}')

c8q3dHDx4 = Parameter(name = 'c8q3dHDx4',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3dHDx4Re + c8q3dHDx4Im*complex(0,1)',
                      texname = '\\text{c8q3dHDx4}')

c8q3dHDx5 = Parameter(name = 'c8q3dHDx5',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3dHDx5Re + c8q3dHDx5Im*complex(0,1)',
                      texname = '\\text{c8q3dHDx5}')

c8q3dHDx6 = Parameter(name = 'c8q3dHDx6',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8q3dHDx6Re + c8q3dHDx6Im*complex(0,1)',
                      texname = '\\text{c8q3dHDx6}')

c8qu2dHDx1 = Parameter(name = 'c8qu2dHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qu2dHDx1Re + c8qu2dHDx1Im*complex(0,1)',
                       texname = '\\text{c8qu2dHDx1}')

c8qu2dHDx2 = Parameter(name = 'c8qu2dHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qu2dHDx2Re + c8qu2dHDx2Im*complex(0,1)',
                       texname = '\\text{c8qu2dHDx2}')

c8qu2dHDx3 = Parameter(name = 'c8qu2dHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qu2dHDx3Re + c8qu2dHDx3Im*complex(0,1)',
                       texname = '\\text{c8qu2dHDx3}')

c8qu2dHDx4 = Parameter(name = 'c8qu2dHDx4',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qu2dHDx4Re + c8qu2dHDx4Im*complex(0,1)',
                       texname = '\\text{c8qu2dHDx4}')

c8qu2dHDx5 = Parameter(name = 'c8qu2dHDx5',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qu2dHDx5Re + c8qu2dHDx5Im*complex(0,1)',
                       texname = '\\text{c8qu2dHDx5}')

c8qu2dHDx6 = Parameter(name = 'c8qu2dHDx6',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8qu2dHDx6Re + c8qu2dHDx6Im*complex(0,1)',
                       texname = '\\text{c8qu2dHDx6}')

c8qd3HDx1 = Parameter(name = 'c8qd3HDx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qd3HDx1Re + c8qd3HDx1Im*complex(0,1)',
                      texname = '\\text{c8qd3HDx1}')

c8qd3HDx2 = Parameter(name = 'c8qd3HDx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qd3HDx2Re + c8qd3HDx2Im*complex(0,1)',
                      texname = '\\text{c8qd3HDx2}')

c8qd3HDx3 = Parameter(name = 'c8qd3HDx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qd3HDx3Re + c8qd3HDx3Im*complex(0,1)',
                      texname = '\\text{c8qd3HDx3}')

c8q2udD2x1 = Parameter(name = 'c8q2udD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udD2x1Re + c8q2udD2x1Im*complex(0,1)',
                       texname = '\\text{c8q2udD2x1}')

c8q2udD2x2 = Parameter(name = 'c8q2udD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udD2x2Re + c8q2udD2x2Im*complex(0,1)',
                       texname = '\\text{c8q2udD2x2}')

c8q2udD2x3 = Parameter(name = 'c8q2udD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8q2udD2x3Re + c8q2udD2x3Im*complex(0,1)',
                       texname = '\\text{c8q2udD2x3}')

c8lequD2x1 = Parameter(name = 'c8lequD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lequD2x1Re + c8lequD2x1Im*complex(0,1)',
                       texname = '\\text{c8lequD2x1}')

c8lequD2x2 = Parameter(name = 'c8lequD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lequD2x2Re + c8lequD2x2Im*complex(0,1)',
                       texname = '\\text{c8lequD2x2}')

c8lequD2x3 = Parameter(name = 'c8lequD2x3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lequD2x3Re + c8lequD2x3Im*complex(0,1)',
                       texname = '\\text{c8lequD2x3}')

c8leG2Hx1 = Parameter(name = 'c8leG2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leG2Hx1Re + c8leG2Hx1Im*complex(0,1)',
                      texname = '\\text{c8leG2Hx1}')

c8leG2Hx2 = Parameter(name = 'c8leG2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leG2Hx2Re + c8leG2Hx2Im*complex(0,1)',
                      texname = '\\text{c8leG2Hx2}')

c8leW2Hx1 = Parameter(name = 'c8leW2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leW2Hx1Re + c8leW2Hx1Im*complex(0,1)',
                      texname = '\\text{c8leW2Hx1}')

c8leW2Hx2 = Parameter(name = 'c8leW2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leW2Hx2Re + c8leW2Hx2Im*complex(0,1)',
                      texname = '\\text{c8leW2Hx2}')

c8leW2Hx3 = Parameter(name = 'c8leW2Hx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leW2Hx3Re + c8leW2Hx3Im*complex(0,1)',
                      texname = '\\text{c8leW2Hx3}')

c8quG2Hx1 = Parameter(name = 'c8quG2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quG2Hx1Re + c8quG2Hx1Im*complex(0,1)',
                      texname = '\\text{c8quG2Hx1}')

c8quG2Hx2 = Parameter(name = 'c8quG2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quG2Hx2Re + c8quG2Hx2Im*complex(0,1)',
                      texname = '\\text{c8quG2Hx2}')

c8quG2Hx3 = Parameter(name = 'c8quG2Hx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quG2Hx3Re + c8quG2Hx3Im*complex(0,1)',
                      texname = '\\text{c8quG2Hx3}')

c8quG2Hx4 = Parameter(name = 'c8quG2Hx4',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quG2Hx4Re + c8quG2Hx4Im*complex(0,1)',
                      texname = '\\text{c8quG2Hx4}')

c8quG2Hx5 = Parameter(name = 'c8quG2Hx5',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quG2Hx5Re + c8quG2Hx5Im*complex(0,1)',
                      texname = '\\text{c8quG2Hx5}')

c8quGWHx1 = Parameter(name = 'c8quGWHx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quGWHx1Re + c8quGWHx1Im*complex(0,1)',
                      texname = '\\text{c8quGWHx1}')

c8quGWHx2 = Parameter(name = 'c8quGWHx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quGWHx2Re + c8quGWHx2Im*complex(0,1)',
                      texname = '\\text{c8quGWHx2}')

c8quGWHx3 = Parameter(name = 'c8quGWHx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quGWHx3Re + c8quGWHx3Im*complex(0,1)',
                      texname = '\\text{c8quGWHx3}')

c8quGBHx1 = Parameter(name = 'c8quGBHx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quGBHx1Re + c8quGBHx1Im*complex(0,1)',
                      texname = '\\text{c8quGBHx1}')

c8quGBHx2 = Parameter(name = 'c8quGBHx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quGBHx2Re + c8quGBHx2Im*complex(0,1)',
                      texname = '\\text{c8quGBHx2}')

c8quGBHx3 = Parameter(name = 'c8quGBHx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quGBHx3Re + c8quGBHx3Im*complex(0,1)',
                      texname = '\\text{c8quGBHx3}')

c8quW2Hx1 = Parameter(name = 'c8quW2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quW2Hx1Re + c8quW2Hx1Im*complex(0,1)',
                      texname = '\\text{c8quW2Hx1}')

c8quW2Hx2 = Parameter(name = 'c8quW2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quW2Hx2Re + c8quW2Hx2Im*complex(0,1)',
                      texname = '\\text{c8quW2Hx2}')

c8quW2Hx3 = Parameter(name = 'c8quW2Hx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quW2Hx3Re + c8quW2Hx3Im*complex(0,1)',
                      texname = '\\text{c8quW2Hx3}')

c8quWBHx3 = Parameter(name = 'c8quWBHx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quWBHx3Re + c8quWBHx3Im*complex(0,1)',
                      texname = '\\text{c8quWBHx3}')

c8quWBHx1 = Parameter(name = 'c8quWBHx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quWBHx1Re + c8quWBHx1Im*complex(0,1)',
                      texname = '\\text{c8quWBHx1}')

c8quWBHx2 = Parameter(name = 'c8quWBHx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quWBHx2Re + c8quWBHx2Im*complex(0,1)',
                      texname = '\\text{c8quWBHx2}')

c8quB2Hx1 = Parameter(name = 'c8quB2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quB2Hx1Re + c8quB2Hx1Im*complex(0,1)',
                      texname = '\\text{c8quB2Hx1}')

c8quB2Hx2 = Parameter(name = 'c8quB2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8quB2Hx2Re + c8quB2Hx2Im*complex(0,1)',
                      texname = '\\text{c8quB2Hx2}')

c8leWBHx1 = Parameter(name = 'c8leWBHx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leWBHx1Re + c8leWBHx1Im*complex(0,1)',
                      texname = '\\text{c8leWBHx1}')

c8leWBHx2 = Parameter(name = 'c8leWBHx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leWBHx2Re + c8leWBHx2Im*complex(0,1)',
                      texname = '\\text{c8leWBHx2}')

c8leWBHx3 = Parameter(name = 'c8leWBHx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leWBHx3Re + c8leWBHx3Im*complex(0,1)',
                      texname = '\\text{c8leWBHx3}')

c8leB2Hx1 = Parameter(name = 'c8leB2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leB2Hx1Re + c8leB2Hx1Im*complex(0,1)',
                      texname = '\\text{c8leB2Hx1}')

c8leB2Hx2 = Parameter(name = 'c8leB2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8leB2Hx2Re + c8leB2Hx2Im*complex(0,1)',
                      texname = '\\text{c8leB2Hx2}')

c8qdG2Hx1 = Parameter(name = 'c8qdG2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdG2Hx1Re + c8qdG2Hx1Im*complex(0,1)',
                      texname = '\\text{c8qdG2Hx1}')

c8qdG2Hx2 = Parameter(name = 'c8qdG2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdG2Hx2Re + c8qdG2Hx2Im*complex(0,1)',
                      texname = '\\text{c8qdG2Hx2}')

c8qdG2Hx3 = Parameter(name = 'c8qdG2Hx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdG2Hx3Re + c8qdG2Hx3Im*complex(0,1)',
                      texname = '\\text{c8qdG2Hx3}')

c8qdG2Hx4 = Parameter(name = 'c8qdG2Hx4',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdG2Hx4Re + c8qdG2Hx4Im*complex(0,1)',
                      texname = '\\text{c8qdG2Hx4}')

c8qdG2Hx5 = Parameter(name = 'c8qdG2Hx5',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdG2Hx5Re + c8qdG2Hx5Im*complex(0,1)',
                      texname = '\\text{c8qdG2Hx5}')

c8qdGWHx1 = Parameter(name = 'c8qdGWHx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdGWHx1Re + c8qdGWHx1Im*complex(0,1)',
                      texname = '\\text{c8qdGWHx1}')

c8qdGWHx2 = Parameter(name = 'c8qdGWHx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdGWHx2Re + c8qdGWHx2Im*complex(0,1)',
                      texname = '\\text{c8qdGWHx2}')

c8qdGWHx3 = Parameter(name = 'c8qdGWHx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdGWHx3Re + c8qdGWHx3Im*complex(0,1)',
                      texname = '\\text{c8qdGWHx3}')

c8qdGBHx1 = Parameter(name = 'c8qdGBHx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdGBHx1Re + c8qdGBHx1Im*complex(0,1)',
                      texname = '\\text{c8qdGBHx1}')

c8qdGBHx2 = Parameter(name = 'c8qdGBHx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdGBHx2Re + c8qdGBHx2Im*complex(0,1)',
                      texname = '\\text{c8qdGBHx2}')

c8qdGBHx3 = Parameter(name = 'c8qdGBHx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdGBHx3Re + c8qdGBHx3Im*complex(0,1)',
                      texname = '\\text{c8qdGBHx3}')

c8qdW2Hx1 = Parameter(name = 'c8qdW2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdW2Hx1Re + c8qdW2Hx1Im*complex(0,1)',
                      texname = '\\text{c8qdW2Hx1}')

c8qdW2Hx2 = Parameter(name = 'c8qdW2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdW2Hx2Re + c8qdW2Hx2Im*complex(0,1)',
                      texname = '\\text{c8qdW2Hx2}')

c8qdW2Hx3 = Parameter(name = 'c8qdW2Hx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdW2Hx3Re + c8qdW2Hx3Im*complex(0,1)',
                      texname = '\\text{c8qdW2Hx3}')

c8qdWBHx1 = Parameter(name = 'c8qdWBHx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdWBHx1Re + c8qdWBHx1Im*complex(0,1)',
                      texname = '\\text{c8qdWBHx1}')

c8qdWBHx2 = Parameter(name = 'c8qdWBHx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdWBHx2Re + c8qdWBHx2Im*complex(0,1)',
                      texname = '\\text{c8qdWBHx2}')

c8qdWBHx3 = Parameter(name = 'c8qdWBHx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdWBHx3Re + c8qdWBHx3Im*complex(0,1)',
                      texname = '\\text{c8qdWBHx3}')

c8qdB2Hx1 = Parameter(name = 'c8qdB2Hx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdB2Hx1Re + c8qdB2Hx1Im*complex(0,1)',
                      texname = '\\text{c8qdB2Hx1}')

c8qdB2Hx2 = Parameter(name = 'c8qdB2Hx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8qdB2Hx2Re + c8qdB2Hx2Im*complex(0,1)',
                      texname = '\\text{c8qdB2Hx2}')

c8lqudH2x1 = Parameter(name = 'c8lqudH2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lqudH2x1Re + c8lqudH2x1Im*complex(0,1)',
                       texname = '\\text{c8lqudH2x1}')

c8lqudH2x2 = Parameter(name = 'c8lqudH2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lqudH2x2Re + c8lqudH2x2Im*complex(0,1)',
                       texname = '\\text{c8lqudH2x2}')

c8eq2uH2 = Parameter(name = 'c8eq2uH2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8eq2uH2Re + c8eq2uH2Im*complex(0,1)',
                     texname = '\\text{c8eq2uH2}')

c8lq3H2x1 = Parameter(name = 'c8lq3H2x1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lq3H2x1Re + c8lq3H2x1Im*complex(0,1)',
                      texname = '\\text{c8lq3H2x1}')

c8lq3H2x2 = Parameter(name = 'c8lq3H2x2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lq3H2x2Re + c8lq3H2x2Im*complex(0,1)',
                      texname = '\\text{c8lq3H2x2}')

c8eu2dH2 = Parameter(name = 'c8eu2dH2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8eu2dH2Re + c8eu2dH2Im*complex(0,1)',
                     texname = '\\text{c8eu2dH2}')

c8lq3H2x3 = Parameter(name = 'c8lq3H2x3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lq3H2x3Re + c8lq3H2x3Im*complex(0,1)',
                      texname = '\\text{c8lq3H2x3}')

c8lqu2H2 = Parameter(name = 'c8lqu2H2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lqu2H2Re + c8lqu2H2Im*complex(0,1)',
                     texname = '\\text{c8lqu2H2}')

c8lqd2H2 = Parameter(name = 'c8lqd2H2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lqd2H2Re + c8lqd2H2Im*complex(0,1)',
                     texname = '\\text{c8lqd2H2}')

c8eq2dH2 = Parameter(name = 'c8eq2dH2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8eq2dH2Re + c8eq2dH2Im*complex(0,1)',
                     texname = '\\text{c8eq2dH2}')

c8lqudD2x1 = Parameter(name = 'c8lqudD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lqudD2x1Re + c8lqudD2x1Im*complex(0,1)',
                       texname = '\\text{c8lqudD2x1}')

c8lqudD2x2 = Parameter(name = 'c8lqudD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lqudD2x2Re + c8lqudD2x2Im*complex(0,1)',
                       texname = '\\text{c8lqudD2x2}')

c8eq2uD2 = Parameter(name = 'c8eq2uD2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8eq2uD2Re + c8eq2uD2Im*complex(0,1)',
                     texname = '\\text{c8eq2uD2}')

c8lq3D2 = Parameter(name = 'c8lq3D2',
                    nature = 'internal',
                    type = 'complex',
                    value = 'c8lq3D2Re + c8lq3D2Im*complex(0,1)',
                    texname = '\\text{c8lq3D2}')

c8eu2dD2x1 = Parameter(name = 'c8eu2dD2x1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8eu2dD2x1Re + c8eu2dD2x1Im*complex(0,1)',
                       texname = '\\text{c8eu2dD2x1}')

c8eu2dD2x2 = Parameter(name = 'c8eu2dD2x2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8eu2dD2x2Re + c8eu2dD2x2Im*complex(0,1)',
                       texname = '\\text{c8eu2dD2x2}')

c8lqudGx1 = Parameter(name = 'c8lqudGx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lqudGx1Re + c8lqudGx1Im*complex(0,1)',
                      texname = '\\text{c8lqudGx1}')

c8lqudGx2 = Parameter(name = 'c8lqudGx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lqudGx2Re + c8lqudGx2Im*complex(0,1)',
                      texname = '\\text{c8lqudGx2}')

c8lqudGx3 = Parameter(name = 'c8lqudGx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lqudGx3Re + c8lqudGx3Im*complex(0,1)',
                      texname = '\\text{c8lqudGx3}')

c8lqudGx4 = Parameter(name = 'c8lqudGx4',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lqudGx4Re + c8lqudGx4Im*complex(0,1)',
                      texname = '\\text{c8lqudGx4}')

c8lqudWx1 = Parameter(name = 'c8lqudWx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lqudWx1Re + c8lqudWx1Im*complex(0,1)',
                      texname = '\\text{c8lqudWx1}')

c8lqudWx2 = Parameter(name = 'c8lqudWx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lqudWx2Re + c8lqudWx2Im*complex(0,1)',
                      texname = '\\text{c8lqudWx2}')

c8lqudBx1 = Parameter(name = 'c8lqudBx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lqudBx1Re + c8lqudBx1Im*complex(0,1)',
                      texname = '\\text{c8lqudBx1}')

c8lqudBx2 = Parameter(name = 'c8lqudBx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8lqudBx2Re + c8lqudBx2Im*complex(0,1)',
                      texname = '\\text{c8lqudBx2}')

c8eq2uGx1 = Parameter(name = 'c8eq2uGx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eq2uGx1Re + c8eq2uGx1Im*complex(0,1)',
                      texname = '\\text{c8eq2uGx1}')

c8eq2uGx2 = Parameter(name = 'c8eq2uGx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eq2uGx2Re + c8eq2uGx2Im*complex(0,1)',
                      texname = '\\text{c8eq2uGx2}')

c8eq2uWx1 = Parameter(name = 'c8eq2uWx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eq2uWx1Re + c8eq2uWx1Im*complex(0,1)',
                      texname = '\\text{c8eq2uWx1}')

c8eq2uBx1 = Parameter(name = 'c8eq2uBx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eq2uBx1Re + c8eq2uBx1Im*complex(0,1)',
                      texname = '\\text{c8eq2uBx1}')

c8lq3Gx1 = Parameter(name = 'c8lq3Gx1',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Gx1Re + c8lq3Gx1Im*complex(0,1)',
                     texname = '\\text{c8lq3Gx1}')

c8lq3Gx2 = Parameter(name = 'c8lq3Gx2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Gx2Re + c8lq3Gx2Im*complex(0,1)',
                     texname = '\\text{c8lq3Gx2}')

c8lq3Wx1 = Parameter(name = 'c8lq3Wx1',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Wx1Re + c8lq3Wx1Im*complex(0,1)',
                     texname = '\\text{c8lq3Wx1}')

c8lq3Wx2 = Parameter(name = 'c8lq3Wx2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Wx2Re + c8lq3Wx2Im*complex(0,1)',
                     texname = '\\text{c8lq3Wx2}')

c8lq3Bx1 = Parameter(name = 'c8lq3Bx1',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Bx1Re + c8lq3Bx1Im*complex(0,1)',
                     texname = '\\text{c8lq3Bx1}')

c8eu2dGx1 = Parameter(name = 'c8eu2dGx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eu2dGx1Re + c8eu2dGx1Im*complex(0,1)',
                      texname = '\\text{c8eu2dGx1}')

c8eu2dGx2 = Parameter(name = 'c8eu2dGx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eu2dGx2Re + c8eu2dGx2Im*complex(0,1)',
                      texname = '\\text{c8eu2dGx2}')

c8eu2dGx3 = Parameter(name = 'c8eu2dGx3',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eu2dGx3Re + c8eu2dGx3Im*complex(0,1)',
                      texname = '\\text{c8eu2dGx3}')

c8eu2dBx1 = Parameter(name = 'c8eu2dBx1',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eu2dBx1Re + c8eu2dBx1Im*complex(0,1)',
                      texname = '\\text{c8eu2dBx1}')

c8eu2dBx2 = Parameter(name = 'c8eu2dBx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eu2dBx2Re + c8eu2dBx2Im*complex(0,1)',
                      texname = '\\text{c8eu2dBx2}')

c8eq2uWx2 = Parameter(name = 'c8eq2uWx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eq2uWx2Re + c8eq2uWx2Im*complex(0,1)',
                      texname = '\\text{c8eq2uWx2}')

c8eq2uBx2 = Parameter(name = 'c8eq2uBx2',
                      nature = 'internal',
                      type = 'complex',
                      value = 'c8eq2uBx2Re + c8eq2uBx2Im*complex(0,1)',
                      texname = '\\text{c8eq2uBx2}')

c8lq3Gx3 = Parameter(name = 'c8lq3Gx3',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Gx3Re + c8lq3Gx3Im*complex(0,1)',
                     texname = '\\text{c8lq3Gx3}')

c8lq3Gx4 = Parameter(name = 'c8lq3Gx4',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Gx4Re + c8lq3Gx4Im*complex(0,1)',
                     texname = '\\text{c8lq3Gx4}')

c8lq3Wx3 = Parameter(name = 'c8lq3Wx3',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Wx3Re + c8lq3Wx3Im*complex(0,1)',
                     texname = '\\text{c8lq3Wx3}')

c8lq3Bx2 = Parameter(name = 'c8lq3Bx2',
                     nature = 'internal',
                     type = 'complex',
                     value = 'c8lq3Bx2Re + c8lq3Bx2Im*complex(0,1)',
                     texname = '\\text{c8lq3Bx2}')

c8lu2dHDx1 = Parameter(name = 'c8lu2dHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lu2dHDx1Re + c8lu2dHDx1Im*complex(0,1)',
                       texname = '\\text{c8lu2dHDx1}')

c8lu2dHDx2 = Parameter(name = 'c8lu2dHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lu2dHDx2Re + c8lu2dHDx2Im*complex(0,1)',
                       texname = '\\text{c8lu2dHDx2}')

c8lud2HDx1 = Parameter(name = 'c8lud2HDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lud2HDx1Re + c8lud2HDx1Im*complex(0,1)',
                       texname = '\\text{c8lud2HDx1}')

c8lud2HDx2 = Parameter(name = 'c8lud2HDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lud2HDx2Re + c8lud2HDx2Im*complex(0,1)',
                       texname = '\\text{c8lud2HDx2}')

c8lq2uHDx1 = Parameter(name = 'c8lq2uHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lq2uHDx1Re + c8lq2uHDx1Im*complex(0,1)',
                       texname = '\\text{c8lq2uHDx1}')

c8lq2uHDx2 = Parameter(name = 'c8lq2uHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lq2uHDx2Re + c8lq2uHDx2Im*complex(0,1)',
                       texname = '\\text{c8lq2uHDx2}')

c8lq2uHDx3 = Parameter(name = 'c8lq2uHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lq2uHDx3Re + c8lq2uHDx3Im*complex(0,1)',
                       texname = '\\text{c8lq2uHDx3}')

c8lq2dHDx1 = Parameter(name = 'c8lq2dHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lq2dHDx1Re + c8lq2dHDx1Im*complex(0,1)',
                       texname = '\\text{c8lq2dHDx1}')

c8lq2dHDx2 = Parameter(name = 'c8lq2dHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lq2dHDx2Re + c8lq2dHDx2Im*complex(0,1)',
                       texname = '\\text{c8lq2dHDx2}')

c8lq2dHDx3 = Parameter(name = 'c8lq2dHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8lq2dHDx3Re + c8lq2dHDx3Im*complex(0,1)',
                       texname = '\\text{c8lq2dHDx3}')

c8eq3HD = Parameter(name = 'c8eq3HD',
                    nature = 'internal',
                    type = 'complex',
                    value = 'c8eq3HDRe + c8eq3HDIm*complex(0,1)',
                    texname = '\\text{c8eq3HD}')

c8equ2HDx1 = Parameter(name = 'c8equ2HDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8equ2HDx1Re + c8equ2HDx1Im*complex(0,1)',
                       texname = '\\text{c8equ2HDx1}')

c8equ2HDx2 = Parameter(name = 'c8equ2HDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8equ2HDx2Re + c8equ2HDx2Im*complex(0,1)',
                       texname = '\\text{c8equ2HDx2}')

c8equdHDx1 = Parameter(name = 'c8equdHDx1',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8equdHDx1Re + c8equdHDx1Im*complex(0,1)',
                       texname = '\\text{c8equdHDx1}')

c8equdHDx2 = Parameter(name = 'c8equdHDx2',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8equdHDx2Re + c8equdHDx2Im*complex(0,1)',
                       texname = '\\text{c8equdHDx2}')

c8equdHDx3 = Parameter(name = 'c8equdHDx3',
                       nature = 'internal',
                       type = 'complex',
                       value = 'c8equdHDx3Re + c8equdHDx3Im*complex(0,1)',
                       texname = '\\text{c8equdHDx3}')

sw2SM = Parameter(name = 'sw2SM',
                  nature = 'internal',
                  type = 'real',
                  value = '(1 - cmath.sqrt(1 - (2*aEW*cmath.pi*cmath.sqrt(2))/(Gf*MZ**2)))/2.',
                  texname = '\\text{sw2SM}')

Zh2 = Parameter(name = 'Zh2',
                nature = 'internal',
                type = 'real',
                value = '1 - 2*cHbox*L6*vevSM**2 + (cHDD*L6*vevSM**2)/2. + ((c8H6x1 + c8H6x2)*L8*vevSM**4)/4.',
                texname = '\\text{Zh2}')

ee = Parameter(name = 'ee',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi)',
               texname = 'e')

rh1 = Parameter(name = 'rh1',
                nature = 'internal',
                type = 'real',
                value = '-0.25*((-4*cHbox + cHDD)*L6*vevSM**2)',
                texname = '\\text{rh1}')

rh2 = Parameter(name = 'rh2',
                nature = 'internal',
                type = 'real',
                value = '(3*cHbox**2*L6**2*vevSM**4)/2. - (3*cHbox*cHDD*L6**2*vevSM**4)/4. + (3*cHDD**2*L6**2*vevSM**4)/32. + 2*cHbox*cHl3*L6**2*vevSM**4 - (cHDD*cHl3*L6**2*vevSM**4)/2. - cHbox*cll1*L6**2*vevSM**4 + (cHDD*cll1*L6**2*vevSM**4)/4. - (c8H6x1*L8*vevSM**4)/8. - (c8H6x2*L8*vevSM**4)/8.',
                texname = '\\text{rh2}')

rW1 = Parameter(name = 'rW1',
                nature = 'internal',
                type = 'real',
                value = 'cHW*L6*vevSM**2',
                texname = '\\text{rW1}')

rW2 = Parameter(name = 'rW2',
                nature = 'internal',
                type = 'real',
                value = '2*cHl3*cHW*L6**2*vevSM**4 + (3*cHW**2*L6**2*vevSM**4)/2. - cHW*cll1*L6**2*vevSM**4 + (c8W2H4x1*L8*vevSM**4)/2.',
                texname = '\\text{rW2}')

vev = Parameter(name = 'vev',
                nature = 'internal',
                type = 'real',
                value = 'vevSM',
                texname = '\\text{vev}')

vev1 = Parameter(name = 'vev1',
                 nature = 'internal',
                 type = 'real',
                 value = '((2*cHl3 - cll1)*L6*vevSM**2)/2.',
                 texname = '\\text{vev1}')

vev2 = Parameter(name = 'vev2',
                 nature = 'internal',
                 type = 'real',
                 value = '2*cHl3**2*L6**2*vevSM**4 - (3*cHl3*cll1*L6**2*vevSM**4)/2. + (3*cll1**2*L6**2*vevSM**4)/8. - (c8H6x1*L8*vevSM**4)/8. + (c8H6x2*L8*vevSM**4)/8. + (c8l2H4Dx2*L8*vevSM**4)/2. + (c8l2H4Dx4*L8*vevSM**4)/2.',
                 texname = '\\text{vev2}')

sw2 = Parameter(name = 'sw2',
                nature = 'internal',
                type = 'real',
                value = 'sw2SM',
                texname = '\\text{sw2}')

d8fB = Parameter(name = 'd8fB',
                 nature = 'internal',
                 type = 'real',
                 value = '(c8B2H4x1*vev**4)/Lam**4',
                 texname = '\\text{d8fB}')

d8fG = Parameter(name = 'd8fG',
                 nature = 'internal',
                 type = 'real',
                 value = '(c8G2H4x1*vev**4)/Lam**4',
                 texname = '\\text{d8fG}')

d8fW = Parameter(name = 'd8fW',
                 nature = 'internal',
                 type = 'real',
                 value = '(c8W2H4x1*vev**4)/Lam**4',
                 texname = '\\text{d8fW}')

d8fW3 = Parameter(name = 'd8fW3',
                  nature = 'internal',
                  type = 'real',
                  value = '((c8W2H4x1 + c8W2H4x3)*vev**4)/Lam**4',
                  texname = '\\text{d8fW3}')

d8fWB = Parameter(name = 'd8fWB',
                  nature = 'internal',
                  type = 'real',
                  value = '(c8WBH4x1*vev**4)/(2.*Lam**4)',
                  texname = '\\text{d8fWB}')

d8gWl = Parameter(name = 'd8gWl',
                  nature = 'internal',
                  type = 'real',
                  value = '((c8l2H4Dx2 + c8l2H4Dx4)*vev**4)/(2.*Lam**4)',
                  texname = '\\text{d8gWl}')

d8mW = Parameter(name = 'd8mW',
                 nature = 'internal',
                 type = 'real',
                 value = '((c8H6x1 - c8H6x2)*vev**4)/(4.*Lam**4)',
                 texname = '\\text{d8mW}')

d8mZ = Parameter(name = 'd8mZ',
                 nature = 'internal',
                 type = 'real',
                 value = '((c8H6x1 + c8H6x2)*vev**4)/(4.*Lam**4)',
                 texname = '\\text{d8mZ}')

d8Zh = Parameter(name = 'd8Zh',
                 nature = 'internal',
                 type = 'real',
                 value = '((c8H6x1 + c8H6x2)*vev**4)/(4.*Lam**4)',
                 texname = '\\text{d8Zh}')

g1SM = Parameter(name = 'g1SM',
                 nature = 'internal',
                 type = 'real',
                 value = '(2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi))/cmath.sqrt(1 - sw2SM)',
                 texname = '\\text{g1SM}')

gwSM = Parameter(name = 'gwSM',
                 nature = 'internal',
                 type = 'real',
                 value = '(2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi))/cmath.sqrt(sw2SM)',
                 texname = '\\text{gwSM}')

vevT = Parameter(name = 'vevT',
                 nature = 'internal',
                 type = 'real',
                 value = '(1 + vev1 + vev2)*vevSM',
                 texname = '\\text{vevT}')

cw = Parameter(name = 'cw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(1 - sw2)',
               texname = 'c_w')

MW2SM = Parameter(name = 'MW2SM',
                  nature = 'internal',
                  type = 'real',
                  value = '(gwSM**2*vevSM**2)/4.',
                  texname = '\\text{MW2SM}')

sw = Parameter(name = 'sw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(sw2)',
               texname = 's_w')

g11 = Parameter(name = 'g11',
                nature = 'internal',
                type = 'real',
                value = '-0.25*((4*cHB*g1SM**2 + cHDD*g1SM**2 + 4*cHl3*g1SM**2 - 2*cll1*g1SM**2 + 4*cHWB*g1SM*gwSM - 4*cHB*gwSM**2)*L6*vevSM**2)/((g1SM - gwSM)*(g1SM + gwSM))',
                texname = '\\text{g11}')

g12 = Parameter(name = 'g12',
                nature = 'internal',
                type = 'real',
                value = '(-16*cHB**2*g1SM**6*L6**2*vevSM**4 + 8*cHB*cHDD*g1SM**6*L6**2*vevSM**4 + 3*cHDD**2*g1SM**6*L6**2*vevSM**4 - 32*cHB*cHl3*g1SM**6*L6**2*vevSM**4 - 8*cHDD*cHl3*g1SM**6*L6**2*vevSM**4 - 32*cHl3**2*g1SM**6*L6**2*vevSM**4 - 16*cHWB**2*g1SM**6*L6**2*vevSM**4 + 16*cHB*cll1*g1SM**6*L6**2*vevSM**4 + 4*cHDD*cll1*g1SM**6*L6**2*vevSM**4 + 16*cHl3*cll1*g1SM**6*L6**2*vevSM**4 - 4*cll1**2*g1SM**6*L6**2*vevSM**4 - 64*cHl3*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 - 32*cHW*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 + 32*cHWB*cll1*g1SM**5*gwSM*L6**2*vevSM**4 + 48*cHB**2*g1SM**4*gwSM**2*L6**2*vevSM**4 - 16*cHB*cHDD*g1SM**4*gwSM**2*L6**2*vevSM**4 - 7*cHDD**2*g1SM**4*gwSM**2*L6**2*vevSM**4 + 128*cHB*cHl3*g1SM**4*gwSM**2*L6**2*vevSM**4 + 8*cHDD*cHl3*g1SM**4*gwSM**2*L6**2*vevSM**4 + 48*cHl3**2*g1SM**4*gwSM**2*L6**2*vevSM**4 + 16*cHWB**2*g1SM**4*gwSM**2*L6**2*vevSM**4 - 64*cHB*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4 - 4*cHDD*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4 - 16*cHl3*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4 + 4*cll1**2*g1SM**4*gwSM**2*L6**2*vevSM**4 - 24*cHDD*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 + 32*cHl3*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 + 64*cHW*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 - 16*cHWB*cll1*g1SM**3*gwSM**3*L6**2*vevSM**4 - 48*cHB**2*g1SM**2*gwSM**4*L6**2*vevSM**4 + 8*cHB*cHDD*g1SM**2*gwSM**4*L6**2*vevSM**4 - 160*cHB*cHl3*g1SM**2*gwSM**4*L6**2*vevSM**4 - 32*cHDD*cHl3*g1SM**2*gwSM**4*L6**2*vevSM**4 - 80*cHl3**2*g1SM**2*gwSM**4*L6**2*vevSM**4 - 64*cHWB**2*g1SM**2*gwSM**4*L6**2*vevSM**4 + 80*cHB*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4 + 16*cHDD*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4 + 64*cHl3*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4 - 16*cll1**2*g1SM**2*gwSM**4*L6**2*vevSM**4 - 8*cHDD*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 - 96*cHl3*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 - 32*cHW*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 + 48*cHWB*cll1*g1SM*gwSM**5*L6**2*vevSM**4 + 16*cHB**2*gwSM**6*L6**2*vevSM**4 + 64*cHB*cHl3*gwSM**6*L6**2*vevSM**4 - 32*cHB*cll1*gwSM**6*L6**2*vevSM**4 - 16*c8B2H4x1*g1SM**6*L8*vevSM**4 - 8*c8H6x2*g1SM**6*L8*vevSM**4 - 16*c8l2H4Dx2*g1SM**6*L8*vevSM**4 - 16*c8l2H4Dx4*g1SM**6*L8*vevSM**4 - 16*c8WBH4x1*g1SM**5*gwSM*L8*vevSM**4 + 48*c8B2H4x1*g1SM**4*gwSM**2*L8*vevSM**4 + 16*c8H6x2*g1SM**4*gwSM**2*L8*vevSM**4 + 32*c8l2H4Dx2*g1SM**4*gwSM**2*L8*vevSM**4 + 32*c8l2H4Dx4*g1SM**4*gwSM**2*L8*vevSM**4 + 32*c8WBH4x1*g1SM**3*gwSM**3*L8*vevSM**4 - 48*c8B2H4x1*g1SM**2*gwSM**4*L8*vevSM**4 - 8*c8H6x2*g1SM**2*gwSM**4*L8*vevSM**4 - 16*c8l2H4Dx2*g1SM**2*gwSM**4*L8*vevSM**4 - 16*c8l2H4Dx4*g1SM**2*gwSM**4*L8*vevSM**4 - 16*c8WBH4x1*g1SM*gwSM**5*L8*vevSM**4 + 16*c8B2H4x1*gwSM**6*L8*vevSM**4)/(32*g1SM**6 - 96*g1SM**4*gwSM**2 + 96*g1SM**2*gwSM**4 - 32*gwSM**6)',
                texname = '\\text{g12}')

gw1 = Parameter(name = 'gw1',
                nature = 'internal',
                type = 'real',
                value = '((-4*cHW*g1SM**2 + 4*cHWB*g1SM*gwSM + cHDD*gwSM**2 + 4*cHl3*gwSM**2 + 4*cHW*gwSM**2 - 2*cll1*gwSM**2)*L6*vevSM**2)/(4.*(g1SM - gwSM)*(g1SM + gwSM))',
                texname = '\\text{gw1}')

gw2 = Parameter(name = 'gw2',
                nature = 'internal',
                type = 'real',
                value = '(-64*cHl3*cHW*g1SM**6*L6**2*vevSM**4 - 16*cHW**2*g1SM**6*L6**2*vevSM**4 + 32*cHW*cll1*g1SM**6*L6**2*vevSM**4 + 32*cHB*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 + 8*cHDD*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 + 96*cHl3*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 - 48*cHWB*cll1*g1SM**5*gwSM*L6**2*vevSM**4 + 32*cHDD*cHl3*g1SM**4*gwSM**2*L6**2*vevSM**4 + 80*cHl3**2*g1SM**4*gwSM**2*L6**2*vevSM**4 - 8*cHDD*cHW*g1SM**4*gwSM**2*L6**2*vevSM**4 + 160*cHl3*cHW*g1SM**4*gwSM**2*L6**2*vevSM**4 + 48*cHW**2*g1SM**4*gwSM**2*L6**2*vevSM**4 + 64*cHWB**2*g1SM**4*gwSM**2*L6**2*vevSM**4 - 16*cHDD*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4 - 64*cHl3*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4 - 80*cHW*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4 + 16*cll1**2*g1SM**4*gwSM**2*L6**2*vevSM**4 - 64*cHB*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 + 24*cHDD*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 - 32*cHl3*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 + 16*cHWB*cll1*g1SM**3*gwSM**3*L6**2*vevSM**4 + 7*cHDD**2*g1SM**2*gwSM**4*L6**2*vevSM**4 - 8*cHDD*cHl3*g1SM**2*gwSM**4*L6**2*vevSM**4 - 48*cHl3**2*g1SM**2*gwSM**4*L6**2*vevSM**4 + 16*cHDD*cHW*g1SM**2*gwSM**4*L6**2*vevSM**4 - 128*cHl3*cHW*g1SM**2*gwSM**4*L6**2*vevSM**4 - 48*cHW**2*g1SM**2*gwSM**4*L6**2*vevSM**4 - 16*cHWB**2*g1SM**2*gwSM**4*L6**2*vevSM**4 + 4*cHDD*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4 + 16*cHl3*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4 + 64*cHW*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4 - 4*cll1**2*g1SM**2*gwSM**4*L6**2*vevSM**4 + 32*cHB*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 + 64*cHl3*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 - 32*cHWB*cll1*g1SM*gwSM**5*L6**2*vevSM**4 - 3*cHDD**2*gwSM**6*L6**2*vevSM**4 + 8*cHDD*cHl3*gwSM**6*L6**2*vevSM**4 + 32*cHl3**2*gwSM**6*L6**2*vevSM**4 - 8*cHDD*cHW*gwSM**6*L6**2*vevSM**4 + 32*cHl3*cHW*gwSM**6*L6**2*vevSM**4 + 16*cHW**2*gwSM**6*L6**2*vevSM**4 + 16*cHWB**2*gwSM**6*L6**2*vevSM**4 - 4*cHDD*cll1*gwSM**6*L6**2*vevSM**4 - 16*cHl3*cll1*gwSM**6*L6**2*vevSM**4 - 16*cHW*cll1*gwSM**6*L6**2*vevSM**4 + 4*cll1**2*gwSM**6*L6**2*vevSM**4 - 16*c8W2H4x1*g1SM**6*L8*vevSM**4 - 16*c8W2H4x3*g1SM**6*L8*vevSM**4 + 16*c8WBH4x1*g1SM**5*gwSM*L8*vevSM**4 + 8*c8H6x2*g1SM**4*gwSM**2*L8*vevSM**4 + 16*c8l2H4Dx2*g1SM**4*gwSM**2*L8*vevSM**4 + 16*c8l2H4Dx4*g1SM**4*gwSM**2*L8*vevSM**4 + 48*c8W2H4x1*g1SM**4*gwSM**2*L8*vevSM**4 + 48*c8W2H4x3*g1SM**4*gwSM**2*L8*vevSM**4 - 32*c8WBH4x1*g1SM**3*gwSM**3*L8*vevSM**4 - 16*c8H6x2*g1SM**2*gwSM**4*L8*vevSM**4 - 32*c8l2H4Dx2*g1SM**2*gwSM**4*L8*vevSM**4 - 32*c8l2H4Dx4*g1SM**2*gwSM**4*L8*vevSM**4 - 48*c8W2H4x1*g1SM**2*gwSM**4*L8*vevSM**4 - 48*c8W2H4x3*g1SM**2*gwSM**4*L8*vevSM**4 + 16*c8WBH4x1*g1SM*gwSM**5*L8*vevSM**4 + 8*c8H6x2*gwSM**6*L8*vevSM**4 + 16*c8l2H4Dx2*gwSM**6*L8*vevSM**4 + 16*c8l2H4Dx4*gwSM**6*L8*vevSM**4 + 16*c8W2H4x1*gwSM**6*L8*vevSM**4 + 16*c8W2H4x3*gwSM**6*L8*vevSM**4)/(32*g1SM**6 - 96*g1SM**4*gwSM**2 + 96*g1SM**2*gwSM**4 - 32*gwSM**6)',
                texname = '\\text{gw2}')

lam = Parameter(name = 'lam',
                nature = 'internal',
                type = 'real',
                value = '(3*cH*L6*vevT**2 + 3*c8H8*L8*vevT**4 + (MH**2*Zh2)/vevT**2)/2.',
                texname = '\\text{lam}')

MW21 = Parameter(name = 'MW21',
                 nature = 'internal',
                 type = 'real',
                 value = '((4*cHl3*g1SM**2 - 2*cll1*g1SM**2 + 4*cHWB*g1SM*gwSM + cHDD*gwSM**2)*L6*vevSM**2)/(2.*(g1SM - gwSM)*(g1SM + gwSM))',
                 texname = '\\text{MW21}')

MW22 = Parameter(name = 'MW22',
                 nature = 'internal',
                 type = 'real',
                 value = '(20*cHl3**2*g1SM**6*L6**2*vevSM**4 - 16*cHl3*cll1*g1SM**6*L6**2*vevSM**4 + 4*cll1**2*g1SM**6*L6**2*vevSM**4 + 8*cHB*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 + 2*cHDD*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 + 40*cHl3*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 + 8*cHW*cHWB*g1SM**5*gwSM*L6**2*vevSM**4 - 20*cHWB*cll1*g1SM**5*gwSM*L6**2*vevSM**4 + 12*cHDD*cHl3*g1SM**4*gwSM**2*L6**2*vevSM**4 - 24*cHl3**2*g1SM**4*gwSM**2*L6**2*vevSM**4 + 20*cHWB**2*g1SM**4*gwSM**2*L6**2*vevSM**4 - 6*cHDD*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4 + 16*cHl3*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4 - 4*cll1**2*g1SM**4*gwSM**2*L6**2*vevSM**4 - 16*cHB*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 + 8*cHDD*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 - 32*cHl3*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 - 16*cHW*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4 + 16*cHWB*cll1*g1SM**3*gwSM**3*L6**2*vevSM**4 + 2*cHDD**2*g1SM**2*gwSM**4*L6**2*vevSM**4 - 8*cHDD*cHl3*g1SM**2*gwSM**4*L6**2*vevSM**4 + 20*cHl3**2*g1SM**2*gwSM**4*L6**2*vevSM**4 - 8*cHWB**2*g1SM**2*gwSM**4*L6**2*vevSM**4 + 4*cHDD*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4 - 16*cHl3*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4 + 4*cll1**2*g1SM**2*gwSM**4*L6**2*vevSM**4 + 8*cHB*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 - 2*cHDD*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 + 24*cHl3*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 + 8*cHW*cHWB*g1SM*gwSM**5*L6**2*vevSM**4 - 12*cHWB*cll1*g1SM*gwSM**5*L6**2*vevSM**4 - cHDD**2*gwSM**6*L6**2*vevSM**4 + 4*cHDD*cHl3*gwSM**6*L6**2*vevSM**4 + 4*cHWB**2*gwSM**6*L6**2*vevSM**4 - 2*cHDD*cll1*gwSM**6*L6**2*vevSM**4 + 4*c8l2H4Dx2*g1SM**6*L8*vevSM**4 + 4*c8l2H4Dx4*g1SM**6*L8*vevSM**4 - 4*c8W2H4x3*g1SM**6*L8*vevSM**4 + 4*c8WBH4x1*g1SM**5*gwSM*L8*vevSM**4 + 2*c8H6x2*g1SM**4*gwSM**2*L8*vevSM**4 - 8*c8l2H4Dx2*g1SM**4*gwSM**2*L8*vevSM**4 - 8*c8l2H4Dx4*g1SM**4*gwSM**2*L8*vevSM**4 + 12*c8W2H4x3*g1SM**4*gwSM**2*L8*vevSM**4 - 8*c8WBH4x1*g1SM**3*gwSM**3*L8*vevSM**4 - 4*c8H6x2*g1SM**2*gwSM**4*L8*vevSM**4 + 4*c8l2H4Dx2*g1SM**2*gwSM**4*L8*vevSM**4 + 4*c8l2H4Dx4*g1SM**2*gwSM**4*L8*vevSM**4 - 12*c8W2H4x3*g1SM**2*gwSM**4*L8*vevSM**4 + 4*c8WBH4x1*g1SM*gwSM**5*L8*vevSM**4 + 2*c8H6x2*gwSM**6*L8*vevSM**4 + 4*c8W2H4x3*gwSM**6*L8*vevSM**4)/(4*g1SM**6 - 12*g1SM**4*gwSM**2 + 12*g1SM**2*gwSM**4 - 4*gwSM**6)',
                 texname = '\\text{MW22}')

TAA1 = Parameter(name = 'TAA1',
                 nature = 'internal',
                 type = 'real',
                 value = '((cHW*g1SM**2 - cHWB*g1SM*gwSM + cHB*gwSM**2)*L6*vevSM**2)/(g1SM**2 + gwSM**2)',
                 texname = '\\text{TAA1}')

TAA2 = Parameter(name = 'TAA2',
                 nature = 'internal',
                 type = 'real',
                 value = '(64*cHl3*cHW*g1SM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHW**2*g1SM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHW*cll1*g1SM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHB*cHWB*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHDD*cHWB*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (96*cHl3*cHWB*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (64*cHW*cHWB*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHWB*cll1*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHB**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (8*cHB*cHDD*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (cHDD**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (96*cHB*cHl3*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHDD*cHl3*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*cHl3**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHDD*cHW*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (160*cHl3*cHW*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (96*cHW**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*cHWB**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (48*cHB*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (4*cHDD*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*cHl3*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (80*cHW*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (4*cll1**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (96*cHB*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (128*cHl3*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (96*cHW*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (64*cHWB*cll1*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (96*cHB**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHB*cHDD*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (cHDD**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (160*cHB*cHl3*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHDD*cHl3*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*cHl3**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (8*cHDD*cHW*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (96*cHl3*cHW*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHW**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*cHWB**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (80*cHB*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (4*cHDD*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*cHl3*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (48*cHW*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (4*cll1**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (64*cHB*cHWB*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHDD*cHWB*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (96*cHl3*cHWB*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHW*cHWB*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHWB*cll1*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHB**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (64*cHB*cHl3*gwSM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHB*cll1*gwSM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8W2H4x1*g1SM**6*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8W2H4x3*g1SM**6*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*c8WBH4x1*g1SM**5*gwSM*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8B2H4x1*g1SM**4*gwSM**2*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*c8W2H4x1*g1SM**4*gwSM**2*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*c8W2H4x3*g1SM**4*gwSM**2*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (32*c8WBH4x1*g1SM**3*gwSM**3*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*c8B2H4x1*g1SM**2*gwSM**4*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8W2H4x1*g1SM**2*gwSM**4*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8W2H4x3*g1SM**2*gwSM**4*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*c8WBH4x1*g1SM*gwSM**5*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8B2H4x1*gwSM**6*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6)',
                 texname = '\\text{TAA2}')

TAZ1 = Parameter(name = 'TAZ1',
                 nature = 'internal',
                 type = 'real',
                 value = '-0.25*((-4*cHWB*g1SM**4 + 4*cHB*g1SM**3*gwSM - cHDD*g1SM**3*gwSM - 4*cHl3*g1SM**3*gwSM - 4*cHW*g1SM**3*gwSM + 2*cll1*g1SM**3*gwSM - 4*cHB*g1SM*gwSM**3 - cHDD*g1SM*gwSM**3 - 4*cHl3*g1SM*gwSM**3 + 4*cHW*g1SM*gwSM**3 + 2*cll1*g1SM*gwSM**3 - 4*cHWB*gwSM**4)*L6*vevSM**2)/((g1SM - gwSM)*(g1SM + gwSM)*(g1SM**2 + gwSM**2))',
                 texname = '\\text{TAZ1}')

TAZ2 = Parameter(name = 'TAZ2',
                 nature = 'internal',
                 type = 'real',
                 value = '(32*cHB*cHWB*g1SM**8*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*cHl3*cHWB*g1SM**8*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*cHW*cHWB*g1SM**8*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (32*cHWB*cll1*g1SM**8*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHB**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (cHDD**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (64*cHB*cHl3*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (24*cHDD*cHl3*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*cHl3**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*cHDD*cHW*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (96*cHl3*cHW*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHW**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHWB**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (32*cHB*cll1*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (12*cHDD*cll1*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHl3*cll1*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHW*cll1*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (12*cll1**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (64*cHB*cHWB*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*cHDD*cHWB*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHl3*cHWB*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (128*cHW*cHWB*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHWB*cll1*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (144*cHB**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*cHB*cHDD*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (5*cHDD**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (224*cHB*cHl3*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*cHDD*cHl3*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHDD*cHW*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (256*cHl3*cHW*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (144*cHW**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (80*cHWB**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (112*cHB*cll1*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (4*cHDD*cll1*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHl3*cll1*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (128*cHW*cll1*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (4*cll1**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (96*cHB*cHWB*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHDD*cHWB*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (320*cHl3*cHWB*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (96*cHW*cHWB*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (160*cHWB*cll1*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (144*cHB**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHB*cHDD*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (5*cHDD**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (256*cHB*cHl3*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*cHDD*cHl3*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*cHDD*cHW*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (224*cHl3*cHW*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (144*cHW**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (80*cHWB**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (128*cHB*cll1*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (4*cHDD*cll1*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHl3*cll1*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (112*cHW*cll1*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (4*cll1**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (128*cHB*cHWB*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*cHDD*cHWB*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHl3*cHWB*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (64*cHW*cHWB*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHWB*cll1*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHB**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*cHB*cHDD*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (cHDD**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (96*cHB*cHl3*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (24*cHDD*cHl3*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*cHl3**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (64*cHl3*cHW*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHW**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHWB**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHB*cll1*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (12*cHDD*cll1*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHl3*cll1*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (32*cHW*cll1*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (12*cll1**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*cHB*cHWB*gwSM**8*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*cHl3*cHWB*gwSM**8*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (32*cHW*cHWB*gwSM**8*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (32*cHWB*cll1*gwSM**8*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8WBH4x1*g1SM**8*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8B2H4x1*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*c8H6x2*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8l2H4Dx2*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8l2H4Dx4*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8W2H4x1*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8W2H4x3*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (32*c8WBH4x1*g1SM**6*gwSM**2*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*c8B2H4x1*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*c8H6x2*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8l2H4Dx2*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8l2H4Dx4*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*c8W2H4x1*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*c8W2H4x3*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (32*c8WBH4x1*g1SM**4*gwSM**4*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*c8B2H4x1*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*c8H6x2*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8l2H4Dx2*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8l2H4Dx4*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*c8W2H4x1*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*c8W2H4x3*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (32*c8WBH4x1*g1SM**2*gwSM**6*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8B2H4x1*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*c8H6x2*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8l2H4Dx2*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8l2H4Dx4*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8W2H4x1*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8W2H4x3*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8WBH4x1*gwSM**8*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8)',
                 texname = '\\text{TAZ2}')

TZA1 = Parameter(name = 'TZA1',
                 nature = 'internal',
                 type = 'real',
                 value = '-0.25*(g1SM*gwSM*(4*cHB*g1SM**2 + cHDD*g1SM**2 + 4*cHl3*g1SM**2 - 4*cHW*g1SM**2 - 2*cll1*g1SM**2 + 8*cHWB*g1SM*gwSM - 4*cHB*gwSM**2 + cHDD*gwSM**2 + 4*cHl3*gwSM**2 + 4*cHW*gwSM**2 - 2*cll1*gwSM**2)*L6*vevSM**2)/((g1SM - gwSM)*(g1SM + gwSM)*(g1SM**2 + gwSM**2))',
                 texname = '\\text{TZA1}')

TZA2 = Parameter(name = 'TZA2',
                 nature = 'internal',
                 type = 'real',
                 value = '(-48*cHB**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*cHB*cHDD*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (cHDD**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHB*cHl3*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (24*cHDD*cHl3*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (64*cHl3**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*cHl3*cHW*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHW**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHWB**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHB*cll1*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (12*cHDD*cll1*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHl3*cll1*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (32*cHW*cll1*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (12*cll1**2*g1SM**7*gwSM*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHB*cHWB*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (24*cHDD*cHWB*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (224*cHl3*cHWB*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHW*cHWB*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (112*cHWB*cll1*g1SM**6*gwSM**2*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (144*cHB**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*cHB*cHDD*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (5*cHDD**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (256*cHB*cHl3*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*cHDD*cHl3*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*cHDD*cHW*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (224*cHl3*cHW*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (144*cHW**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHWB**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (128*cHB*cll1*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (4*cHDD*cll1*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*cHl3*cll1*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (112*cHW*cll1*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (4*cll1**2*g1SM**5*gwSM**3*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (192*cHB*cHWB*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHDD*cHWB*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (192*cHl3*cHWB*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (192*cHW*cHWB*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHWB*cll1*g1SM**4*gwSM**4*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (144*cHB**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*cHB*cHDD*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (5*cHDD**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (224*cHB*cHl3*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*cHDD*cHl3*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*cHDD*cHW*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (256*cHl3*cHW*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (144*cHW**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHWB**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (112*cHB*cll1*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (4*cHDD*cll1*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*cHl3*cll1*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (128*cHW*cll1*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (4*cll1**2*g1SM**3*gwSM**5*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHB*cHWB*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (24*cHDD*cHWB*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (224*cHl3*cHWB*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHW*cHWB*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (112*cHWB*cll1*g1SM**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHB**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (cHDD**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*cHB*cHl3*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (24*cHDD*cHl3*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (64*cHl3**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*cHDD*cHW*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (96*cHl3*cHW*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*cHW**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*cHWB**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (32*cHB*cll1*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (12*cHDD*cll1*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHl3*cll1*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*cHW*cll1*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (12*cll1**2*g1SM*gwSM**7*L6**2*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8B2H4x1*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*c8H6x2*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8l2H4Dx2*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8l2H4Dx4*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8W2H4x1*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8W2H4x3*g1SM**7*gwSM*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (32*c8WBH4x1*g1SM**6*gwSM**2*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*c8B2H4x1*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*c8H6x2*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8l2H4Dx2*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8l2H4Dx4*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*c8W2H4x1*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*c8W2H4x3*g1SM**5*gwSM**3*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (64*c8WBH4x1*g1SM**4*gwSM**4*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (48*c8B2H4x1*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (8*c8H6x2*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8l2H4Dx2*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8l2H4Dx4*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*c8W2H4x1*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (48*c8W2H4x3*g1SM**3*gwSM**5*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (32*c8WBH4x1*g1SM**2*gwSM**6*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) + (16*c8B2H4x1*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (8*c8H6x2*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8l2H4Dx2*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8l2H4Dx4*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8W2H4x1*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8) - (16*c8W2H4x3*g1SM*gwSM**7*L8*vevSM**4)/(32*g1SM**8 - 64*g1SM**6*gwSM**2 + 64*g1SM**2*gwSM**6 - 32*gwSM**8)',
                 texname = '\\text{TZA2}')

TZZ1 = Parameter(name = 'TZZ1',
                 nature = 'internal',
                 type = 'real',
                 value = '((cHB*g1SM**2 + cHWB*g1SM*gwSM + cHW*gwSM**2)*L6*vevSM**2)/(g1SM**2 + gwSM**2)',
                 texname = '\\text{TZZ1}')

TZZ2 = Parameter(name = 'TZZ2',
                 nature = 'internal',
                 type = 'real',
                 value = '(48*cHB**2*g1SM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (64*cHB*cHl3*g1SM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*cHWB**2*g1SM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHB*cll1*g1SM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (32*cHB*cHWB*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (64*cHl3*cHWB*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (64*cHW*cHWB*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHWB*cll1*g1SM**5*gwSM*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (96*cHB**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHB*cHDD*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (cHDD**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (160*cHB*cHl3*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHDD*cHl3*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*cHl3**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (8*cHDD*cHW*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (96*cHl3*cHW*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHW**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHWB**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (80*cHB*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (4*cHDD*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*cHl3*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (48*cHW*cll1*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (4*cll1**2*g1SM**4*gwSM**2*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (96*cHB*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*cHDD*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (192*cHl3*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (96*cHW*cHWB*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (96*cHWB*cll1*g1SM**3*gwSM**3*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHB**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (8*cHB*cHDD*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (cHDD**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (96*cHB*cHl3*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHDD*cHl3*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (16*cHl3**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (8*cHDD*cHW*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (160*cHl3*cHW*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (96*cHW**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHWB**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (48*cHB*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (4*cHDD*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*cHl3*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (80*cHW*cll1*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (4*cll1**2*g1SM**2*gwSM**4*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (64*cHB*cHWB*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (64*cHl3*cHWB*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (32*cHW*cHWB*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHWB*cll1*g1SM*gwSM**5*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (64*cHl3*cHW*gwSM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (48*cHW**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*cHWB**2*gwSM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*cHW*cll1*gwSM**6*L6**2*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8B2H4x1*g1SM**6*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8WBH4x1*g1SM**5*gwSM*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*c8B2H4x1*g1SM**4*gwSM**2*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8W2H4x1*g1SM**4*gwSM**2*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8W2H4x3*g1SM**4*gwSM**2*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*c8WBH4x1*g1SM**3*gwSM**3*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8B2H4x1*g1SM**2*gwSM**4*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*c8W2H4x1*g1SM**2*gwSM**4*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) - (32*c8W2H4x3*g1SM**2*gwSM**4*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8WBH4x1*g1SM*gwSM**5*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8W2H4x1*gwSM**6*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6) + (16*c8W2H4x3*gwSM**6*L8*vevSM**4)/(32*g1SM**6 - 32*g1SM**4*gwSM**2 - 32*g1SM**2*gwSM**4 + 32*gwSM**6)',
                 texname = '\\text{TZZ2}')

yb = Parameter(name = 'yb',
               nature = 'internal',
               type = 'real',
               value = '(c8qdH5*L8*vevT**4)/4. + (ymb*cmath.sqrt(2))/vevT',
               texname = '\\text{yb}')

yc = Parameter(name = 'yc',
               nature = 'internal',
               type = 'real',
               value = '(c8quH5*L8*vevT**4)/4. + (ymc*cmath.sqrt(2))/vevT',
               texname = '\\text{yc}')

ydo = Parameter(name = 'ydo',
                nature = 'internal',
                type = 'real',
                value = '(c8qdH5*L8*vevT**4)/4. + (ymdo*cmath.sqrt(2))/vevT',
                texname = '\\text{ydo}')

ye = Parameter(name = 'ye',
               nature = 'internal',
               type = 'real',
               value = '(c8leH5*L8*vevT**4)/4. + (yme*cmath.sqrt(2))/vevT',
               texname = '\\text{ye}')

ym = Parameter(name = 'ym',
               nature = 'internal',
               type = 'real',
               value = '(c8leH5*L8*vevT**4)/4. + (ymm*cmath.sqrt(2))/vevT',
               texname = '\\text{ym}')

ys = Parameter(name = 'ys',
               nature = 'internal',
               type = 'real',
               value = '(c8qdH5*L8*vevT**4)/4. + (yms*cmath.sqrt(2))/vevT',
               texname = '\\text{ys}')

yt = Parameter(name = 'yt',
               nature = 'internal',
               type = 'real',
               value = '(c8quH5*L8*vevT**4)/4. + (ymt*cmath.sqrt(2))/vevT',
               texname = '\\text{yt}')

ytau = Parameter(name = 'ytau',
                 nature = 'internal',
                 type = 'real',
                 value = '(c8leH5*L8*vevT**4)/4. + (ymtau*cmath.sqrt(2))/vevT',
                 texname = '\\text{ytau}')

yup = Parameter(name = 'yup',
                nature = 'internal',
                type = 'real',
                value = '(c8quH5*L8*vevT**4)/4. + (ymup*cmath.sqrt(2))/vevT',
                texname = '\\text{yup}')

muH = Parameter(name = 'muH',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sqrt(lam*vevT**2 - (3*cH*L6*vevT**4)/4. - (c8H8*L8*vevT**6)/2.)',
                texname = '\\mu')

MW = Parameter(name = 'MW',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt((1 + MW21 + MW22)*MW2SM)',
               texname = 'M_W')

g1 = Parameter(name = 'g1',
               nature = 'internal',
               type = 'real',
               value = '(1 + g11 + g12)*g1SM',
               texname = 'g_1')

gw = Parameter(name = 'gw',
               nature = 'internal',
               type = 'real',
               value = '(1 + gw1 + gw2)*gwSM',
               texname = 'g_w')

