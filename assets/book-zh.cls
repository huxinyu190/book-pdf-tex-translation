%%% ============================================================
%%%  dftbook.cls
%%%  《Density Functional Theory: An Advanced Course》
%%%  （R. M. Dreizler & E. K. U. Gross）中译排版模板
%%%
%%%  编译方式：xelatex（需两遍，目录依赖 .toc）
%%%
%%%  用法：
%%%    \documentclass{dftbook}          % 可选选项透传给 ctexbook
%%%    \begin{document}
%%%      \frontmatter
%%%      \tableofcontents               % 前置部分自动套镜像页眉
%%%      \mainmatter
%%%      \chapter{引言}                 % 章标题自动按原书版式排版
%%%      ...
%%%    \end{document}
%%%
%%%  已自动处理：正文小四/行距 22 磅、镜像奇偶页眉、目录条目样式、
%%%  章标题复刻原书版式、公式按章编号 (1.1)…、数学记号宏。
%%% ============================================================

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{dftbook}[2026/09/12 v1.0 DFT 中译排版模板]

% 未识别的选项一律透传给基类
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexbook}}
\ProcessOptions\relax

% ============================================================
% 基类与选项
%   linespread=1：ctex 默认 \baselinestretch=1.3，会把 22pt 行距乘成 28.5pt
%   twoside：奇偶页眉必须区分左右页，oneside 下 fancyhdr 的 E/O 选项不生效
%   openany：\chapter 不再强制起奇数页
% ============================================================
\LoadClass[12pt,a4paper,twoside,openany,linespread=1]{ctexbook}

\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{bm}
\RequirePackage{mathrsfs}   % \mathscr（原书用花体表示集合，如 V、G）
\RequirePackage{geometry}
\RequirePackage{enumitem}
\RequirePackage{newtxmath}
\RequirePackage{pdfpages}   % 原书封面整页导入
\RequirePackage{xcolor}
\RequirePackage{caption}
% 图注：五号、加粗
\DeclareCaptionFont{dftcap}{\zihao{5}\bfseries}
\captionsetup{font=dftcap, labelsep=quad}
\RequirePackage{framed}     % shaded 环境：原书定理陈述的灰底框
\definecolor{shadecolor}{gray}{0.92}   % shaded 环境所要求的底色
\RequirePackage[hidelinks]{hyperref}

\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}

% ============================================================
% 奇偶页眉（镜像式）：页码始终靠外侧，章标题始终靠内侧
%   奇数页(右页)：章标题在左 | 页码在右
%   偶数页(左页)：页码在左 | 章标题在右
% ============================================================
\RequirePackage{fancyhdr}
% twoside 下禁止插空白页（\chapter 与 \mainmatter 都会调 \cleardoublepage）
\let\cleardoublepage\clearpage

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[LO]{\zihao{-5}\songti\leftmark}   % 奇数页·左：章标题
\fancyhead[RO]{\zihao{-5}\songti\thepage}    % 奇数页·右：页码
\fancyhead[RE]{\zihao{-5}\songti\leftmark}   % 偶数页·右：章标题
\fancyhead[LE]{\zihao{-5}\songti\thepage}    % 偶数页·左：页码

% \chapter* 硬编码 \thispagestyle{plain}，且 \thispagestyle 只登记样式名，
% \ps@plain 要到页面 shipout 时才解析。故此处备份原 plain，供前置部分临时改指 fancy。
\let\origpsplain\ps@plain

% ============================================================
% 正文：小四 (12pt)，行距 22 磅
% 直接重定义 \normalsize，使任何 \normalsize 调用都回到 22pt 基线距，
% 避免章节标题等处重置字号后行距被改回默认值。
% ============================================================
\linespread{1}
\renewcommand\normalsize{%
  \@setfontsize\normalsize{12pt}{22pt}%
  \abovedisplayskip 12\p@ \@plus3\p@ \@minus7\p@
  \abovedisplayshortskip \z@ \@plus3\p@
  \belowdisplayshortskip 6.5\p@ \@plus3.5\p@ \@minus3\p@
  \belowdisplayskip \abovedisplayskip
  \let\@listi\@listI}
\normalsize

% ============================================================
% 章节标题样式
% ============================================================
\RequirePackage{titletoc}
\RequirePackage{titleref}
\RequirePackage{titlesec}
\RequirePackage{setspace}

% ------------------------------------------------------------
% 章标题：复刻原书（Springer TMP 版式）
%   原书实测：页面 155x235mm，章标题 13.95pt 粗体，左边界 54.1pt，
%   距页顶 52.3pt（几乎贴着正文块顶端），正文从 223.8pt 才开始。
%   特征 = 编号与标题分两行 + 左对齐 + 粗体 + 无装饰线 + 标题下大片留白。
%   \chapter*（目录标题）走同一个 format，原书 Contents 页同样是左对齐大留白。
% 注：键值里不能直接写 \par 或 \\，会被 ctex 的键解析器吃掉并报
%     "Paragraph ended before \@chapter was complete"，须用宏包一层。
% ------------------------------------------------------------
\newcommand{\ctexchapbreak}{\\}
\ctexset{
  chapter={
    format+    = \zihao{-2} \heiti \raggedright,
    % 去掉 name 尾部的 \ \ ，编号紧贴行首
    name       = {第,章},
    number     = \chinese{chapter},
    % 编号后换行 + 间距 + 切到标题字号 → 标题另起一行且更大
    aftername  = \ctexchapbreak\vspace{10pt}\zihao{1},
    beforeskip = 0.5ex plus 0.2ex minus 0.2ex,
    afterskip  = 40pt plus 2pt minus 2pt
  },
  section={
    format+    = \zihao{4} \heiti \raggedright,
    name       = {,\ },
    beforeskip = 1.5ex plus 0.2ex minus 0.2ex,
    afterskip  = 1.5ex plus 0.2ex minus 0.2ex,
    aftername  = \hspace{0pt}
  },
  subsection={
    format+    = \zihao{-4} \heiti \raggedright,
    name       = {,\ },
    beforeskip = 1.5ex plus 0.2ex minus 0.2ex,
    afterskip  = 1.5ex plus 0.2ex minus 0.2ex,
    aftername  = \hspace{0pt}
  },
  subsubsection={
    format+    = \zihao{-4} \songti \raggedright,
    name       = {,\ },
    beforeskip = 1.5ex plus 0.2ex minus 0.2ex,
    afterskip  = 1.5ex plus 0.2ex minus 0.2ex,
    aftername  = \hspace{0pt}
  }
}

% ---- 编号形式 ----
% 章标题显示为「第一章」，但计数器一律用阿拉伯数字，
% 以保证公式编号为 (1.1)…、节编号为 1.1/1.1.1。
\renewcommand{\thechapter}{\arabic{chapter}}
\renewcommand{\thesection}{\arabic{chapter}.\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}
\renewcommand{\thesubsubsection}{\thesubsection.\arabic{subsubsection}}
\renewcommand{\theequation}{\arabic{chapter}.\arabic{equation}}

% ---- 目录条目样式（小四、宋体、点线引导）----
% 注意 titletoc 的 [<left>] 是「正文文字」的左缩进，而不是编号的左缩进：
% \contentslabel{<width>} 的编号框贴在 <left> 的左端，即编号起点 = left - width。
% 因此 left 必须写成「编号起点 + 编号宽度」，否则编号会向左溢出到页边距之外。
% 章：编号「第一章」宽 3em，自左边距起 → left = 0em + 4.5em（留 1.5em 间隙）
% 目录条目字体：小四 (12pt)，行距与正文一致（22 磅）
% 注意 \zihao{-4} 自带 13.76pt 基线距，必须再用 \fontsize 覆盖，否则目录行距是 13.76pt。
\newcommand{\dfttocfont}{\zihao{-4}\fontsize{12pt}{22pt}\selectfont}

\titlecontents{chapter}[4.5em]
  {\addvspace{8pt}\dfttocfont\songti\bfseries}
  {\contentslabel{4.5em}}{}
  {\titlerule*[3pt]{.}\contentspage}
% 节：编号「1.1」自左边距内缩 2em 起，宽 2.6em → left = 2em + 2.6em
\titlecontents{section}[4.6em]
  {\dfttocfont\songti}
  {\contentslabel{2.6em}}{}
  {\titlerule*[3pt]{.}\contentspage}
% 小节：编号「1.1.1」自左边距内缩 4em 起，宽 3.6em → left = 4em + 3.6em
\titlecontents{subsection}[7.6em]
  {\dfttocfont\songti}
  {\contentslabel{3.6em}}{}
  {\titlerule*[3pt]{.}\contentspage}

\renewcommand{\contentsname}{目\hspace{1em}录}

% ============================================================
% 前置部分（目录等）自动套用镜像页眉
%   \tableofcontents 内部是 \chapter*{\contentsname}，会被压回 plain。
%   \thispagestyle{plain} 只登记样式名，\ps@plain 要到页面 shipout 时才被解析，
%   所以必须等 \mainmatter 的 \clearpage 把目录页送出之后，才能还原 plain。
% ============================================================
\let\dftbook@frontmatter\frontmatter
\renewcommand{\frontmatter}{%
  \dftbook@frontmatter
  \let\ps@plain\ps@fancy}

\let\dftbook@mainmatter\mainmatter
\renewcommand{\mainmatter}{%
  \dftbook@mainmatter
  \let\ps@plain\origpsplain}

% \chapter* 不设 \leftmark，不补的话目录页内侧标题位会是空白
\let\dftbook@tableofcontents\tableofcontents
\renewcommand{\tableofcontents}{%
  \dftbook@tableofcontents
  \markboth{\contentsname}{\contentsname}}

% ============================================================
% 记号约定（本书专用，可按需移出到单独文件）
% ============================================================
\newcommand{\vR}{\boldsymbol{R}}          % 核坐标
\newcommand{\vr}{\boldsymbol{r}}          % 电子坐标
\newcommand{\vA}{\boldsymbol{A}}          % 矢势
\newcommand{\vE}{\boldsymbol{E}}          % 电场
\newcommand{\vB}{\boldsymbol{B}}          % 磁场
\newcommand{\vI}{\boldsymbol{I}}          % 核磁矩
\newcommand{\vS}{\boldsymbol{\sigma}}     % 泡利矩阵矢量
\newcommand{\vnabla}{\boldsymbol{\nabla}} % 梯度算符
\newcommand{\vk}{\boldsymbol{k}}          % 波矢
\newcommand{\vq}{\boldsymbol{q}}          % 动量转移
\newcommand{\ext}{\mathrm{ext}}
\newcommand{\dd}{\mathrm{d}}

\endinput
